import ora from 'ora';
import { RoomodesService } from '../services/roomodes.js';
import { FilesystemService } from '../services/filesystem.js';
import { RegistryService } from '../services/registry.js';
import { logger } from '../utils/logger.js';

export async function uninstallCommand(packNames: string[]): Promise<void> {
  logger.title('🗑️  Agent Pack Uninstaller');

  // Initialize services
  const roomodes = new RoomodesService();
  const fs = new FilesystemService();
  const registry = new RegistryService(fs);

  // Check if registry exists
  if (!fs.registryExists()) {
    logger.error('No installed packs found');
    process.exit(1);
  }

  // Validate pack names
  const installedPacks = registry.getAllInstalled();
  const invalidPacks = packNames.filter(name => !installedPacks.includes(name));
  if (invalidPacks.length > 0) {
    logger.error(`Pack(s) not installed: ${invalidPacks.join(', ')}`);
    logger.info(`Installed packs: ${installedPacks.join(', ')}`);
    process.exit(1);
  }

  // Uninstall each pack
  for (const packName of packNames) {
    logger.log('');
    logger.info(`Uninstalling ${packName}...`);

    const spinner = ora('Loading pack info...').start();

    try {
      const packInfo = registry.getPackInfo(packName);
      if (!packInfo) {
        throw new Error(`Pack info not found for ${packName}`);
      }

      spinner.succeed('Loaded pack info');

      if (packInfo.type === 'roo') {
        // ROO PACK UNINSTALLATION
        // Delete rules folders and merged files
        spinner.start('Removing files...');
        
        // 1. Delete agent-specific rules folders
        for (const folder of packInfo.rulesFolders) {
          fs.deleteRulesFolder(folder);
        }
        
        // 2. Delete merged files owned by this pack
        if (packInfo.mergedFiles && packInfo.mergedFiles.length > 0) {
          fs.deleteMergedFiles(packInfo.mergedFiles);
        }
        
        spinner.succeed(`Removed ${packInfo.rulesFolders.length} agent folders and ${packInfo.mergedFiles?.length || 0} merged files`);

        // Remove modes from .roomodes
        spinner.start('Updating .roomodes...');
        const existingContent = fs.readRoomodes();
        if (existingContent) {
          const existingRoomodes = roomodes.parse(existingContent);
          const updatedRoomodes = roomodes.removeModes(existingRoomodes, packInfo.slugs);
          fs.writeRoomodes(roomodes.serialize(updatedRoomodes));
          spinner.succeed(`Removed ${packInfo.slugs.length} modes from .roomodes`);
        } else {
          spinner.warn('.roomodes file not found');
        }

        // Remove from registry
        registry.unregisterPack(packName);

        logger.success(`Successfully uninstalled ${packName}`);
        logger.dim(`  Modes removed: ${packInfo.slugs.join(', ')}`);

      } else if (packInfo.type === 'copilot-cli') {
        // COPILOT CLI PACK UNINSTALLATION
        spinner.start('Removing Copilot CLI files...');
        
        // Delete all installed files
        if (packInfo.copilotCliFiles && packInfo.copilotCliFiles.length > 0) {
          fs.deleteGitHubFiles(packInfo.copilotCliFiles);
        }
        
        spinner.succeed(`Removed ${packInfo.copilotCliFiles?.length || 0} files`);

        // Remove from registry
        registry.unregisterPack(packName);

        logger.success(`Successfully uninstalled ${packName}`);
        logger.dim(`  Type: Copilot CLI agent`);
      }

    } catch (error) {
      spinner.fail(`Failed to uninstall ${packName}`);
      logger.error(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  }

  // Check if any packs remain, if not clean up .roo and .roomodes
  const remainingPacks = registry.getAllInstalled();
  if (remainingPacks.length === 0) {
    logger.log('');
    logger.info('No packs remaining, cleaning up...');
    const spinner = ora('Removing .roo directory...').start();
    fs.deleteRooDirectory();
    spinner.succeed('Removed .roo directory');
    
    spinner.start('Removing .roomodes file...').start();
    fs.deleteRoomodes();
    spinner.succeed('Removed .roomodes file');
  }

  logger.log('');
  logger.success('All packs uninstalled successfully! ✨');
}
