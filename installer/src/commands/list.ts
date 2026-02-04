import ora from 'ora';
import chalk from 'chalk';
import { GitHubService } from '../services/github.js';
import { FilesystemService } from '../services/filesystem.js';
import { RegistryService } from '../services/registry.js';
import { logger } from '../utils/logger.js';
import type { GitHubConfig } from '../types/index.js';

export async function listCommand(options: { repo?: string; branch?: string }): Promise<void> {
  logger.title('📋 Available Agent Packs');

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
  const fs = new FilesystemService();
  const registry = new RegistryService(fs);

  // Fetch available packs
  const spinner = ora('Fetching available packs...').start();
  try {
    const availablePacks = await github.getAvailablePacks();
    spinner.succeed(`Found ${availablePacks.length} available packs`);

    // Get installed packs
    const installedPacks = new Set(registry.getAllInstalled());

    // Display table
    logger.log('');
    for (const pack of availablePacks) {
      const isInstalled = installedPacks.has(pack.name);
      const status = isInstalled ? chalk.green('✓ installed') : chalk.dim('  not installed');
      const packType = pack.type === 'copilot-cli' ? chalk.cyan('[copilot-cli]') : chalk.blue('[roo]');
      
      logger.log(`${status}  ${chalk.bold(pack.name)} ${packType}`);
      if (pack.description) {
        logger.dim(`           ${pack.description}`);
      }

      if (isInstalled) {
        const packInfo = registry.getPackInfo(pack.name);
        if (packInfo) {
          if (packInfo.type === 'roo') {
            logger.dim(`           Version: ${packInfo.version} | Modes: ${packInfo.slugs.length}`);
          } else {
            logger.dim(`           Version: ${packInfo.version} | Type: Copilot CLI agent`);
          }
        }
      }
      logger.log('');
    }

    // Summary
    logger.info(`Total: ${availablePacks.length} packs available, ${installedPacks.size} installed`);

  } catch (error) {
    spinner.fail('Failed to fetch available packs');
    logger.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}