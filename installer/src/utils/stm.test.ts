import test from 'node:test';
import assert from 'node:assert/strict';
import { extractStmGitignoreEntries } from './stm.js';

test('extractStmGitignoreEntries detects STM entries from file paths', () => {
  const entries = extractStmGitignoreEntries([
    { path: '.ralph-stm/state.json' },
    { path: '.github/agents/a.agent.md' }
  ]);

  assert.equal(entries.includes('.ralph-stm/'), true);
});

test('extractStmGitignoreEntries detects STM entries from file content', () => {
  const entries = extractStmGitignoreEntries([
    {
      path: '.github/skills/evidence-integrity/SKILL.md',
      content: 'Any file path containing `.product-brief-agent-stm/` is disallowed.'
    }
  ]);

  assert.equal(entries.includes('.product-brief-agent-stm/'), true);
});

test('extractStmGitignoreEntries deduplicates repeated entries', () => {
  const entries = extractStmGitignoreEntries([
    { path: '.ralph-stm/state.json' },
    { path: '.github/skills/a.md', content: 'See `.ralph-stm/runs/`.' }
  ]);

  const count = entries.filter(entry => entry === '.ralph-stm/').length;
  assert.equal(count, 1);
});
