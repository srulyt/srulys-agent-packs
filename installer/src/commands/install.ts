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

      // Detect pack type
      const availablePack = availablePacks.find(p => p.name === packName);
      if (!availablePack) {
        throw new Error(`Pack ${packName} not found`);
      }
      const packType = availablePack.type;
      
      logger.dim(`Pack type: ${packType}`);
      
      let slugs: string[] = [];
      let rulesFolders: string[] = [];

      if (packType === 'roo') {
        // Find and parse .roomodes file
        const roomodesFile = files.find(f => f.path === '.roomodes');
        if (!roomodesFile) {
          throw new Error('.roomodes file not found in pack');
        }

        const packRoomodes = roomodes.parse(roomodesFile.content);
        slugs = roomodes.getSlugs(packRoomodes);
        rulesFolders = roomodes.extractRulesFolders(packRoomodes);
      }

      // Install based on pack type
      if (packType === 'roo') {
        // ROO PACK INSTALLATION
        spinner.start('Installing files...');
        fs.ensureRooDirectory();

        // Get existing merged files owned by this pack (for reinstall)
        const existingPackInfo = registry.getPackInfo(packName);
        const ownedFiles = new Set<string>(existingPackInfo?.mergedFiles || []);

        // 1. Install mode-specific rules folders (rules-{slug}/) - REPLACE entirely
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

        // 2. Install all other files - MERGE (skip .roomodes, README.md)
        const mergedFiles: string[] = [];
        const filesToMerge = files.filter(f => {
          // Skip .roomodes (handled separately)
          if (f.path === '.roomodes' || f.path === 'README.md') {
            return false;
          }
          // Skip files in rules-{slug}/ folders (already handled)
          if (rulesFolders.some(folder => f.path.startsWith(`.roo/${folder}/`))) {
            return false;
          }
          return true;
        });

        for (const file of filesToMerge) {
          const wasWritten = fs.writeMergedFile(file.path, file.content, ownedFiles);
          if (wasWritten) {
            mergedFiles.push(file.path);
          }
        }

        spinner.succeed(`Installed ${rulesFolders.length} agent-specific folders and ${mergedFiles.length} merged files`);

        // Merge .roomodes
        spinner.start('Updating .roomodes...');
        const roomodesFile = files.find(f => f.path === '.roomodes');
        if (!roomodesFile) {
          throw new Error('.roomodes file not found');
        }
        
        const packRoomodes = roomodes.parse(roomodesFile.content);
        const existingContent = fs.readRoomodes();
        const existingRoomodes = existingContent 
          ? roomodes.parse(existingContent)
          : { customModes: [] };

        const mergedRoomodes = roomodes.merge(existingRoomodes, packRoomodes, packName);
        fs.writeRoomodes(roomodes.serialize(mergedRoomodes));
        spinner.succeed(`Added ${slugs.length} modes to .roomodes`);

        // Update registry
        const version = await github.getLatestCommitHash();
        registry.registerPack(packName, version, 'roo', slugs, rulesFolders, mergedFiles.length > 0 ? mergedFiles : undefined);

        logger.success(`Successfully installed ${packName}`);
        logger.dim(`  Modes: ${slugs.join(', ')}`);
        logger.dim(`  Version: ${version}`);

      } else if (packType === 'copilot-cli') {
        // COPILOT CLI PACK INSTALLATION
        spinner.start('Installing Copilot CLI files...');
        
        const copilotCliFiles: string[] = [];
        
        // 1. Install .github/agents/ and .github/skills/ files
        const githubFiles = files.filter(f => f.path.startsWith('.github/'));
        for (const file of githubFiles) {
          fs.writeGitHubFile(file.path, file.content);
          copilotCliFiles.push(file.path);
        }
        
        // 2. Install loop scripts to project root
        const scriptFiles = files.filter(f => f.path.endsWith('.ps1') || f.path.endsWith('.sh'));
        for (const file of scriptFiles) {
          fs.writeProjectFile(file.path, file.content);
          copilotCliFiles.push(file.path);
        }
        
        spinner.succeed(`Installed ${githubFiles.length} GitHub files and ${scriptFiles.length} scripts`);
        
        // 3. Add to .gitignore
        spinner.start('Updating .gitignore...');
        fs.appendToGitignore(['.ralph-stm/']);
        spinner.succeed('Updated .gitignore');
        
        // Update registry
        const version = await github.getLatestCommitHash();
        registry.registerPack(packName, version, 'copilot-cli', [], [], undefined, copilotCliFiles);
        
        logger.success(`Successfully installed ${packName}`);
        logger.dim(`  Type: Copilot CLI agent`);
        logger.dim(`  Version: ${version}`);
        logger.log('');
        logger.info('To use Ralph, run:');
        logger.dim('  PowerShell: .\\ralph-loop.ps1 -Task "your task"');
        logger.dim('  Bash: ./ralph-loop.sh "your task"');
      }

    } catch (error) {
      spinner.fail(`Failed to install ${packName}`);
      logger.error(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  }

  logger.log('');
  logger.success('All packs installed successfully! 🎉');
}