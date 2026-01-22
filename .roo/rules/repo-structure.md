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
