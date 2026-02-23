# Repository Structure Rules

## Pack Location Constraint

**MANDATORY**: All new agent packs MUST be created under `agent-packs/{pack-name}/`.

The ONLY exception is the root Factory pack which already exists at repository root.

### What This Means

When creating a new agent pack:
- ✅ `agent-packs/my-pack/.roomodes`
- ✅ `agent-packs/my-pack/.roo/rules-*/`
- ❌ `.roomodes` (root level - FORBIDDEN for new packs)
- ❌ `my-pack/.roomodes` (non-standard path - FORBIDDEN)

### Why This Matters

1. **Discoverability**: Users can browse `agent-packs/` to see all available packs
2. **Isolation**: Each pack is self-contained and portable
3. **Git-friendly**: Clear boundaries prevent accidental cross-pack edits
4. **Factory protection**: Root `.roo/` remains for Factory only

## Documentation Requirement

**MANDATORY**: Every new pack MUST have corresponding documentation.

Required documentation deliverables:
1. `docs/{pack-name}.md` - Full pack documentation
2. `docs/README.md` - Updated TOC entry

This is NOT optional. A pack without documentation is incomplete.

## Gitignore Requirement for Memory Directories

**MANDATORY**: When creating agent packs with STM (Short-Term Memory) or LTM (Long-Term Memory) directories, the Factory MUST update the repository `.gitignore` to exclude these directories.

### Memory Directory Patterns

Common STM/LTM directory patterns that MUST be gitignored:

| Pattern Type | Example | Gitignore Entry |
|-------------|---------|-----------------|
| STM suffix | `.{pack-name}-stm/` | `agent-packs/**/*-stm/` |
| LTM suffix | `.{pack-name}-ltm/` | `agent-packs/**/*-ltm/` |
| Memory suffix | `.{pack-name}-memory/` | `agent-packs/**/*-memory/` |
| Custom STM | `.design-studio/` | `agent-packs/**/.design-studio/` |
| Custom LTM | `.knowledge-base/` | `agent-packs/**/.knowledge-base/` |

### Implementation Steps

When Factory Engineer creates an agent pack with memory directories:

1. **Identify memory directories** - Note all STM/LTM directories in the architecture
2. **Check existing patterns** - Verify if `.gitignore` already covers the pattern
3. **Add specific entries** - If not covered by existing wildcards, add explicit entries
4. **Use appropriate scope** - Use `agent-packs/**/` prefix for pack-specific directories

### Gitignore Entry Format

Add entries under the `Agent Pack STM Directories` section in `.gitignore`:

```gitignore
# ===========================================
# Agent Pack STM Directories
# ===========================================

# {Pack Name} - {Description}
agent-packs/**/.{directory-name}/
```

### Why This Matters

1. **Clean repository**: Memory files are runtime artifacts, not source code
2. **Reduced conflicts**: Prevents merge conflicts from session-specific state
3. **Smaller clones**: Users don't download unnecessary transient data
4. **Privacy**: Some STM may contain sensitive user context
