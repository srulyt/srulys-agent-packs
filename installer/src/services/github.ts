import { execCommand, execWithInput, commandExists } from '../utils/exec.js';
import { logger } from '../utils/logger.js';
import type { GitHubConfig, FileContent, TreeEntry, PackInfo, PackType } from '../types/index.js';

export class GitHubService {
  private config: GitHubConfig;
  private token: string | null = null;
  private authRequired: boolean = false;
  private authAttempted: boolean = false;

  constructor(config: GitHubConfig) {
    this.config = config;
  }

  private async getGitHubToken(): Promise<string | null> {
    // Priority 1: Explicit environment variable
    if (process.env.GITHUB_TOKEN) {
      logger.dim('Using GITHUB_TOKEN from environment');
      return process.env.GITHUB_TOKEN;
    }

    // Priority 2: Git Credential Manager (default)
    const gcmToken = await this.getTokenFromGCM();
    if (gcmToken) {
      logger.dim('Using token from Git Credential Manager');
      return gcmToken;
    }

    // Priority 3: No token (public repos only)
    logger.dim('No authentication found - public repos only');
    return null;
  }

  private async getTokenFromGCM(): Promise<string | null> {
    try {
      const input = 'protocol=https\nhost=github.com\n\n';
      const result = await execWithInput('git credential fill', input);
      const match = result.match(/password=([^\n\r]+)/);
      return match ? match[1].trim() : null;
    } catch {
      return null;
    }
  }

  private async getTokenFromGhCli(): Promise<string | null> {
    try {
      if (!(await commandExists('gh'))) {
        return null;
      }
      const token = await execCommand('gh auth token');
      return token || null;
    } catch {
      return null;
    }
  }

  private async doFetch(url: string, headers: Record<string, string>): Promise<Response> {
    return await fetch(url, { headers });
  }

  private async fetch(url: string): Promise<Response> {
    // Lazy authentication: try without auth first, get token on auth error
    if (this.authRequired && !this.authAttempted) {
      this.authAttempted = true;
      this.token = await this.getGitHubToken();
    }

    const headers: Record<string, string> = {
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': '@srulyt/agent-packs'
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    let response = await this.doFetch(url, headers);

    // If auth error or 404 (private repo) and we haven't tried authenticating yet, get token and retry
    if (!response.ok && (response.status === 401 || response.status === 403 || response.status === 404) && !this.authRequired) {
      this.authRequired = true;
      this.authAttempted = true;
      this.token = await this.getGitHubToken();
      
      // Retry with authentication
      if (this.token) {
        headers['Authorization'] = `Bearer ${this.token}`;
        response = await this.doFetch(url, headers);
      } else {
        throw new Error('Authentication required. Repository may be private.');
      }
    }

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status} ${response.statusText}`);
    }

    return response;
  }

  async getAvailablePacks(): Promise<PackInfo[]> {
    const url = `https://api.github.com/repos/${this.config.owner}/${this.config.repo}/contents/agent-packs?ref=${this.config.branch}`;
    const response = await this.fetch(url);
    const items = await response.json() as Array<{ name: string; type: string; path: string }>;

    const packs: PackInfo[] = [];

    for (const item of items) {
      if (item.type === 'dir') {
        try {
          // Detect pack type by checking for characteristic files
          const packType = await this.detectPackType(item.path);
          
          let description = '';
          if (packType === 'roo') {
            const roomodes = await this.getFileContent(`${item.path}/.roomodes`);
            const lines = roomodes.split('\n');
            description = lines.find(l => l.includes('description:'))?.split('description:')[1]?.trim() || '';
            description = description.replace(/^["']|["']$/g, '');
          } else if (packType === 'copilot-cli') {
            // Try to get description from README
            try {
              const readme = await this.getFileContent(`${item.path}/README.md`);
              const lines = readme.split('\n');
              // Get first non-empty line after the title
              const descLine = lines.find((l, idx) => idx > 0 && l.trim() && !l.startsWith('#'));
              description = descLine?.trim() || '';
            } catch {
              description = 'GitHub Copilot CLI agent pack';
            }
          }
          
          packs.push({
            name: item.name,
            description,
            path: item.path,
            slugs: [],
            type: packType
          });
        } catch {
          // Skip packs that can't be detected
        }
      }
    }

    return packs;
  }

  private async detectPackType(packPath: string): Promise<PackType> {
    // Check for .github/agents/ directory (Copilot CLI pack)
    try {
      const tree = await this.getPackTree(packPath.replace('agent-packs/', ''));
      const hasCopilotAgents = tree.some(entry => entry.path.startsWith('.github/agents/'));
      if (hasCopilotAgents) {
        return 'copilot-cli';
      }
    } catch {
      // Continue to check for .roomodes
    }

    // Check for .roomodes file (Roo pack)
    try {
      await this.getFileContent(`${packPath}/.roomodes`);
      return 'roo';
    } catch {
      throw new Error('Unable to detect pack type');
    }
  }

  async getFileContent(path: string): Promise<string> {
    const url = `https://raw.githubusercontent.com/${this.config.owner}/${this.config.repo}/${this.config.branch}/${path}`;
    const response = await this.fetch(url);
    return await response.text();
  }

  async getPackTree(packName: string): Promise<TreeEntry[]> {
    const url = `https://api.github.com/repos/${this.config.owner}/${this.config.repo}/git/trees/${this.config.branch}?recursive=1`;
    const response = await this.fetch(url);
    const data = await response.json() as { tree: Array<{ path: string; type: string; sha: string }> };

    const packPrefix = `agent-packs/${packName}/`;
    
    return data.tree
      .filter(item => item.path.startsWith(packPrefix))
      .map(item => ({
        path: item.path.substring(packPrefix.length),
        type: item.type as 'blob' | 'tree',
        sha: item.sha
      }));
  }

  async getPackFiles(packName: string): Promise<FileContent[]> {
    const tree = await this.getPackTree(packName);
    const files: FileContent[] = [];

    for (const entry of tree) {
      if (entry.type === 'blob') {
        try {
          const content = await this.getFileContent(`agent-packs/${packName}/${entry.path}`);
          files.push({
            path: entry.path,
            content
          });
        } catch (error) {
          logger.warn(`Failed to fetch file: ${entry.path}`);
        }
      }
    }

    return files;
  }

  async getLatestCommitHash(): Promise<string> {
    const url = `https://api.github.com/repos/${this.config.owner}/${this.config.repo}/commits/${this.config.branch}`;
    const response = await this.fetch(url);
    const data = await response.json() as { sha: string };
    return data.sha.substring(0, 7);
  }
}