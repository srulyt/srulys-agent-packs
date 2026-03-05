import test from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import { FilesystemService } from './filesystem.js';

let originalCwd = '';
let tempDir = '';

test.beforeEach(() => {
  originalCwd = process.cwd();
  tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'agent-packs-installer-test-'));
  process.chdir(tempDir);
});

test.afterEach(() => {
  process.chdir(originalCwd);
  fs.rmSync(tempDir, { recursive: true, force: true });
});

test('appendToGitignore adds header and deduplicates entries', () => {
  const service = new FilesystemService();

  service.appendToGitignore(['.product-brief-agent-stm/']);
  service.appendToGitignore(['.product-brief-agent-stm/']);

  const content = fs.readFileSync(path.join(tempDir, '.gitignore'), 'utf-8');
  const headerCount = (content.match(/# Agent Pack: Copilot CLI/g) || []).length;
  const entryCount = (content.match(/\.product-brief-agent-stm\//g) || []).length;

  assert.equal(headerCount, 1);
  assert.equal(entryCount, 1);
});

test('removeFromGitignore removes only targeted STM entry and keeps remaining ones', () => {
  const service = new FilesystemService();

  service.appendToGitignore(['.product-brief-agent-stm/', '.ralph-stm/']);
  service.removeFromGitignore(['.product-brief-agent-stm/']);

  const content = fs.readFileSync(path.join(tempDir, '.gitignore'), 'utf-8');
  assert.equal(content.includes('.product-brief-agent-stm/'), false);
  assert.equal(content.includes('.ralph-stm/'), true);
  assert.equal(content.includes('# Agent Pack: Copilot CLI'), true);
});

test('removeFromGitignore removes orphaned Copilot CLI header when section is empty', () => {
  const service = new FilesystemService();

  service.appendToGitignore(['.product-brief-agent-stm/']);
  service.removeFromGitignore(['.product-brief-agent-stm/']);

  const content = fs.readFileSync(path.join(tempDir, '.gitignore'), 'utf-8');
  assert.equal(content.includes('.product-brief-agent-stm/'), false);
  assert.equal(content.includes('# Agent Pack: Copilot CLI'), false);
});
