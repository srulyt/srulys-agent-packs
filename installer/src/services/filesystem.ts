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

  // Global rules operations (merge, not replace)
  writeGlobalRulesFiles(files: Array<{ path: string; content: string }>): string[] {
    const basePath = path.join(this.cwd, '.roo', 'rules');
    const writtenFiles: string[] = [];
    
    // Create the base folder
    fs.mkdirSync(basePath, { recursive: true });

    // Write each file (only if it doesn't exist - merge behavior)
    for (const file of files) {
      const filePath = path.join(basePath, file.path);
      const fileDir = path.dirname(filePath);
      
      // Ensure directory exists
      if (!fs.existsSync(fileDir)) {
        fs.mkdirSync(fileDir, { recursive: true });
      }
      
      // Only write if file doesn't exist (preserve existing files)
      if (!fs.existsSync(filePath)) {
        fs.writeFileSync(filePath, file.content, 'utf-8');
        writtenFiles.push(file.path);
      }
    }

    return writtenFiles;
  }

  deleteGlobalRulesFiles(filePaths: string[]): void {
    for (const filePath of filePaths) {
      const fullPath = path.join(this.cwd, '.roo', 'rules', filePath);
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