export interface RooMode {
  slug: string;
  name: string;
  description?: string;
  roleDefinition: string;
  whenToUse: string;
  groups: (string | GroupWithRegex)[];
  customInstructions?: string;
  skills?: string[];
  fileRegex?: string;
  source?: string;
}

export interface GroupWithRegex {
  edit?: {
    fileRegex: string;
    description: string;
  };
}

export interface RoomodesFile {
  customModes: RooMode[];
}

export interface PackInfo {
  name: string;
  description: string;
  path: string;
  slugs: string[];
}

export interface PackRegistry {
  installedPacks: {
    [packName: string]: {
      installedAt: string;
      version: string;
      slugs: string[];
      rulesFolders: string[];
      mergedFiles?: string[]; // All merged files (not in rules-{slug}/) owned by this pack
    };
  };
}

export interface GitHubConfig {
  owner: string;
  repo: string;
  branch: string;
}

export interface FileContent {
  path: string;
  content: string;
}

export interface TreeEntry {
  path: string;
  type: 'blob' | 'tree';
  sha: string;
}