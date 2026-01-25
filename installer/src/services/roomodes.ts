import * as YAML from 'yaml';
import type { RoomodesFile, RooMode } from '../types/index.js';

export class RoomodesService {
  parse(content: string): RoomodesFile {
    try {
      const parsed = YAML.parse(content);
      return parsed as RoomodesFile;
    } catch (error) {
      throw new Error(`Failed to parse .roomodes file: ${error}`);
    }
  }

  serialize(roomodes: RoomodesFile): string {
    return YAML.stringify(roomodes);
  }

  merge(existing: RoomodesFile, incoming: RoomodesFile, packName: string): RoomodesFile {
    // Get slugs from incoming modes
    const incomingSlugs = new Set(incoming.customModes.map(m => m.slug));

    // Remove any existing modes with the same slugs (for reinstall)
    const filteredModes = existing.customModes.filter(m => !incomingSlugs.has(m.slug));

    // Add incoming modes
    return {
      customModes: [...filteredModes, ...incoming.customModes]
    };
  }

  removeModes(existing: RoomodesFile, slugs: string[]): RoomodesFile {
    const slugSet = new Set(slugs);
    return {
      customModes: existing.customModes.filter(m => !slugSet.has(m.slug))
    };
  }

  getSlugs(roomodes: RoomodesFile): string[] {
    return roomodes.customModes.map(m => m.slug);
  }

  extractRulesFolders(roomodes: RoomodesFile): string[] {
    const folders: string[] = [];
    
    for (const mode of roomodes.customModes) {
      // Check for rules in customInstructions
      if (mode.customInstructions) {
        const match = mode.customInstructions.match(/\.roo\/rules-([^/]+)\//);
        if (match) {
          folders.push(`rules-${match[1]}`);
        }
      }
      
      // Common pattern: rules-{slug}
      folders.push(`rules-${mode.slug}`);
    }

    return [...new Set(folders)]; // Remove duplicates
  }
}