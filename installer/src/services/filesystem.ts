import * as fs from 'fs';
import * as path from 'path';

export class FilesystemService {
  private readonly cwd: string;

  constructor() {
    this.cwd = process.cwd();
  }

  // .roomodes file operations
  roomodesExists(): boolean {
    return fs.existsSync(path.join(this.cwd, '.roomodes'));
  }

  readRoomodes(): string | null {
    const roomodesPath = path.join(this.cwd, '.roomodes');
    if (!fs.existsSync(roomodesPath)) {
      return null;
    }
    return fs.readFileSync(roomodesPath, 'utf-8');
  }

  writeRoomodes(content: string): void {
    const roomodesPath = path.join(this.cwd, '.roomodes');
    fs.writeFileSync(roomodesPath, content, 'utf-8');
  }

  // .roo directory operations
  rooDirectoryExists(): boolean {
    return fs.existsSync(path.join(this.cwd, '.roo'));
  }

  ensureRooDirectory(): void {
    const rooPath = path.join(this.cwd, '.roo');
    if (!fs.existsSync(rooPath)) {
      fs.mkdirSync(rooPath, { recursive: true });
    }
  }

  // Rules folder operations
  rulesFolderExists(slug: string): boolean {
    return fs.existsSync(path.join(this.cwd, '.roo', slug));
  }

  deleteRulesFolder(slug: string): void {
    const folderPath = path.join(this.cwd, '.roo', slug);
    if (fs.existsSync(folderPath)) {
      fs.rmSync(folderPath, { recursive: true, force: true });
    }
  }

  writeRulesFolder(slug: string, files: Array<{ path: string; content: string }>): void {
    const basePath = path.join(this.cwd, '.roo', slug);
    
    // Create the base folder
    fs.mkdirSync(basePath, { recursive: true });

    // Write each file
    for (const file of files) {
      const filePath = path.join(basePath, file.path);
      const fileDir = path.dirname(filePath);
      
      // Ensure directory exists
      if (!fs.existsSync(fileDir)) {
        fs.mkdirSync(fileDir, { recursive: true });
      }
      
      fs.writeFileSync(filePath, file.content, 'utf-8');
    }
  }

  listRulesFolders(): string[] {
    const rooPath = path.join(this.cwd, '.roo');
    if (!fs.existsSync(rooPath)) {
      return [];
    }

    const items = fs.readdirSync(rooPath, { withFileTypes: true });
    return items
      .filter(item => item.isDirectory() && item.name.startsWith('rules-'))
      .map(item => item.name);
  }

  // Merged files operations (merge behavior - write if owned by this pack or doesn't exist)
  writeMergedFile(filePath: string, content: string, ownedFiles: Set<string>): boolean {
    const fullPath = path.join(this.cwd, filePath);
    const fileDir = path.dirname(fullPath);
    
    // Ensure directory exists
    if (!fs.existsSync(fileDir)) {
      fs.mkdirSync(fileDir, { recursive: true });
    }
    
    // Write if file doesn't exist OR if this pack owns it
    const fileExists = fs.existsSync(fullPath);
    if (!fileExists || ownedFiles.has(filePath)) {
      fs.writeFileSync(fullPath, content, 'utf-8');
      return true; // File was written
    }
    
    return false; // File skipped (owned by another pack)
  }

  deleteMergedFiles(filePaths: string[]): void {
    for (const filePath of filePaths) {
      const fullPath = path.join(this.cwd, filePath);
      if (fs.existsSync(fullPath)) {
        fs.unlinkSync(fullPath);
      }
    }
  }

  deleteRooDirectory(): void {
    const rooPath = path.join(this.cwd, '.roo');
    if (fs.existsSync(rooPath)) {
      fs.rmSync(rooPath, { recursive: true, force: true });
    }
  }

  deleteRoomodes(): void {
    const roomodesPath = path.join(this.cwd, '.roomodes');
    if (fs.existsSync(roomodesPath)) {
      fs.unlinkSync(roomodesPath);
    }
  }

  // GitHub Copilot CLI file operations
  writeGitHubFile(relativePath: string, content: string): void {
    const fullPath = path.join(this.cwd, relativePath);
    const fileDir = path.dirname(fullPath);
    
    // Ensure directory exists
    if (!fs.existsSync(fileDir)) {
      fs.mkdirSync(fileDir, { recursive: true });
    }
    
    fs.writeFileSync(fullPath, content, 'utf-8');
  }

  writeProjectFile(fileName: string, content: string): void {
    const fullPath = path.join(this.cwd, fileName);
    fs.writeFileSync(fullPath, content, 'utf-8');
    
    // Make scripts executable on Unix-like systems
    if (fileName.endsWith('.sh') && process.platform !== 'win32') {
      try {
        fs.chmodSync(fullPath, 0o755);
      } catch {
        // Silently fail if chmod doesn't work
      }
    }
  }

  deleteGitHubFiles(filePaths: string[]): void {
    for (const filePath of filePaths) {
      const fullPath = path.join(this.cwd, filePath);
      if (fs.existsSync(fullPath)) {
        fs.unlinkSync(fullPath);
        
        // Try to remove parent directories if empty
        let parentDir = path.dirname(fullPath);
        while (parentDir !== this.cwd) {
          try {
            const files = fs.readdirSync(parentDir);
            if (files.length === 0) {
              fs.rmdirSync(parentDir);
              parentDir = path.dirname(parentDir);
            } else {
              break;
            }
          } catch {
            break;
          }
        }
      }
    }
  }

  appendToGitignore(entries: string[]): void {
    const gitignorePath = path.join(this.cwd, '.gitignore');
    let content = '';
    
    if (fs.existsSync(gitignorePath)) {
      content = fs.readFileSync(gitignorePath, 'utf-8');
    }
    
    const existingEntries = new Set(content.split('\n').map(line => line.trim()));
    const newEntries: string[] = [];
    
    for (const entry of entries) {
      if (!existingEntries.has(entry)) {
        newEntries.push(entry);
      }
    }
    
    if (newEntries.length > 0) {
      if (content && !content.endsWith('\n')) {
        content += '\n';
      }
      content += '\n# Agent Pack: Copilot CLI\n';
      content += newEntries.join('\n') + '\n';
      fs.writeFileSync(gitignorePath, content, 'utf-8');
    }
  }

  // Registry file operations
  registryExists(): boolean {
    return fs.existsSync(path.join(this.cwd, '.roo', '.agent-packs-registry.json'));
  }

  readRegistry(): string | null {
    const registryPath = path.join(this.cwd, '.roo', '.agent-packs-registry.json');
    if (!fs.existsSync(registryPath)) {
      return null;
    }
    return fs.readFileSync(registryPath, 'utf-8');
  }

  writeRegistry(content: string): void {
    this.ensureRooDirectory();
    const registryPath = path.join(this.cwd, '.roo', '.agent-packs-registry.json');
    fs.writeFileSync(registryPath, content, 'utf-8');
  }
}