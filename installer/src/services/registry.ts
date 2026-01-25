import { FilesystemService } from './filesystem.js';
import type { PackRegistry } from '../types/index.js';

export class RegistryService {
  private fs: FilesystemService;

  constructor(fs: FilesystemService) {
    this.fs = fs;
  }

  load(): PackRegistry {
    const content = this.fs.readRegistry();
    if (!content) {
      return { installedPacks: {} };
    }

    try {
      return JSON.parse(content) as PackRegistry;
    } catch {
      return { installedPacks: {} };
    }
  }

  save(registry: PackRegistry): void {
    const content = JSON.stringify(registry, null, 2);
    this.fs.writeRegistry(content);
  }

  registerPack(
    packName: string,
    version: string,
    slugs: string[],
    rulesFolders: string[],
    globalRulesFiles?: string[]
  ): void {
    const registry = this.load();
    registry.installedPacks[packName] = {
      installedAt: new Date().toISOString(),
      version,
      slugs,
      rulesFolders,
      globalRulesFiles
    };
    this.save(registry);
  }

  unregisterPack(packName: string): void {
    const registry = this.load();
    delete registry.installedPacks[packName];
    this.save(registry);
  }

  isInstalled(packName: string): boolean {
    const registry = this.load();
    return packName in registry.installedPacks;
  }

  getPackInfo(packName: string) {
    const registry = this.load();
    return registry.installedPacks[packName] || null;
  }

  getAllInstalled(): string[] {
    const registry = this.load();
    return Object.keys(registry.installedPacks);
  }
}