import ora from 'ora';
import { GitHubService } from '../services/github.js';
import { RoomodesService } from '../services/roomodes.js';
import { FilesystemService } from '../services/filesystem.js';
import { RegistryService } from '../services/registry.js';
import { logger } from '../utils/logger.js';
import type { GitHubConfig } from '../types/index.js';

export async function installCommand(
  packNames: string[],
  options: { repo?: string; branch?: string }
): Promise<void> {
  logger.title('📦 Agent Pack Installer');

  // Parse repo option
  const repoMatch = (options.repo || 'srulyt/srulys-agent-packs').match(/^([^/]+)\/([^/]+)$/);
  if (!repoMatch) {
    logger.error('Invalid repository format. Use: owner/repo');
    process.exit(1);
  }

  const config: GitHubConfig = {
    owner: repoMatch[1],
    repo: repoMatch[2],
    branch: options.branch || 'main'
  };

  // Initialize services
  const github = new GitHubService(config);
  const roomodes = new RoomodesService();
  const fs = new FilesystemService();
  const registry = new RegistryService(fs);

  // Get available packs
  const spinner = ora('Fetching available packs...').start();
  let availablePacks;
  try {
    availablePacks = await github.getAvailablePacks();
    spinner.succeed(`Found ${availablePacks.length} available packs`);
  } catch (error) {
    spinner.fail('Failed to fetch available packs');
    logger.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }

  // Validate pack names
  const availablePackNames = new Set(availablePacks.map(p => p.name));
  const invalidPacks = packNames.filter(name => !availablePackNames.has(name));
  if (invalidPacks.length > 0) {
    logger.error(`Invalid pack names: ${invalidPacks.join(', ')}`);
    logger.info(`Available packs: ${[...availablePackNames].join(', ')}`);
    process.exit(1);
  }

  // Install each pack
  for (const packName of packNames) {
    logger.log('');
    logger.info(`Installing ${packName}...`);

    try {
      // Check if already installed
      const isReinstall = registry.isInstalled(packName);
      if (isReinstall) {
        logger.warn(`Pack "${packName}" is already installed. Reinstalling...`);
        const packInfo = registry.getPackInfo(packName);
        if (packInfo) {
          // Delete existing rules folders
          for (const folder of packInfo.rulesFolders) {
            fs.deleteRulesFolder(folder);
          }
        }
      }

      // Fetch pack files
      spinner.start('Fetching pack files...');
      const files = await github.getPackFiles(packName);
      spinner.succeed(`Fetched ${files.length} files`);

      // Find and parse .roomodes file
      const roomodesFile = files.find(f => f.path === '.roomodes');
      if (!roomodesFile) {
        throw new Error('.roomodes file not found in pack');
      }

      const packRoomodes = roomodes.parse(roomodesFile.content);
      const slugs = roomodes.getSlugs(packRoomodes);
      const rulesFolders = roomodes.extractRulesFolders(packRoomodes);

      // Write rules folders
      spinner.start('Installing rules...');
      fs.ensureRooDirectory();

      // Install mode-specific rules (rules-{slug}/)
      for (const folder of rulesFolders) {
        const folderFiles = files.filter(f => f.path.startsWith(`.roo/${folder}/`));
        if (folderFiles.length > 0) {
          const rulesFiles = folderFiles.map(f => ({
            path: f.path.substring(`.roo/${folder}/`.length),
            content: f.content
          }));
          fs.writeRulesFolder(folder, rulesFiles);
        }
      }

      // Install global rules (rules/ folder) - merge, don't replace
      const globalRulesFiles = files.filter(f => f.path.startsWith('.roo/rules/'));
      const writtenGlobalFiles: string[] = [];
      if (globalRulesFiles.length > 0) {
        const globalFiles = globalRulesFiles.map(f => ({
          path: f.path.substring('.roo/rules/'.length),
          content: f.content
        }));
        const written = fs.writeGlobalRulesFiles(globalFiles);
        writtenGlobalFiles.push(...written);
      }

      const totalRules = rulesFolders.length + (writtenGlobalFiles.length > 0 ? 1 : 0);
      spinner.succeed(`Installed ${totalRules} rules folder${totalRules !== 1 ? 's' : ''}`);

      // Merge .roomodes
      spinner.start('Updating .roomodes...');
      const existingContent = fs.readRoomodes();
      const existingRoomodes = existingContent 
        ? roomodes.parse(existingContent)
        : { customModes: [] };

      const mergedRoomodes = roomodes.merge(existingRoomodes, packRoomodes, packName);
      fs.writeRoomodes(roomodes.serialize(mergedRoomodes));
      spinner.succeed(`Added ${slugs.length} modes to .roomodes`);

      // Update registry
      const version = await github.getLatestCommitHash();
      registry.registerPack(packName, version, slugs, rulesFolders, writtenGlobalFiles.length > 0 ? writtenGlobalFiles : undefined);

      logger.success(`Successfully installed ${packName}`);
      logger.dim(`  Modes: ${slugs.join(', ')}`);
      logger.dim(`  Version: ${version}`);

    } catch (error) {
      spinner.fail(`Failed to install ${packName}`);
      logger.error(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  }

  logger.log('');
  logger.success('All packs installed successfully! 🎉');
}