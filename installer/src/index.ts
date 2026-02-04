#!/usr/bin/env node

import { Command } from 'commander';
import { installCommand } from './commands/install.js';
import { uninstallCommand } from './commands/uninstall.js';
import { listCommand } from './commands/list.js';

const program = new Command();

program
  .name('agent-packs')
  .description('CLI installer for Roo Code agent packs')
  .version('1.0.5');

program
  .command('install')
  .description('Install one or more agent packs')
  .argument('<packs...>', 'Pack names to install')
  .option('--repo <repo>', 'GitHub repository (owner/repo)', 'srulyt/srulys-agent-packs')
  .option('--branch <branch>', 'Git branch', 'main')
  .action(installCommand);

program
  .command('uninstall')
  .description('Uninstall one or more agent packs')
  .argument('<packs...>', 'Pack names to uninstall')
  .action(uninstallCommand);

program
  .command('list')
  .description('List available agent packs')
  .option('--repo <repo>', 'GitHub repository (owner/repo)', 'srulyt/srulys-agent-packs')
  .option('--branch <branch>', 'Git branch', 'main')
  .action(listCommand);

program.parse();