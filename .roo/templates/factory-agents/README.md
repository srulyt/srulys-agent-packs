# Factory Agent Templates

This directory contains **FORMAT REFERENCES** for Agent Factory outputs.

**Philosophy**: These are NOT templates to copy—they show structure and syntax only.

## Files

| File | Purpose |
|------|---------|
| [`example-roomode.md`](example-roomode.md) | YAML syntax for `.roomodes` entries |
| [`example-rules.md`](example-rules.md) | Markdown structure for rules files |
| [`response-schemas.md`](response-schemas.md) | JSON schemas for agent responses |
| [`skill-template/SKILL.md`](skill-template/SKILL.md) | Skill file structure |

## Usage Guide

### For Engineers

1. Reference these for **syntax** when implementing
2. Do NOT copy structure—implement what architecture specifies
3. Validate your output parses correctly (YAML, JSON, Markdown)

### For Architects

These files inform what formats are available, not what patterns to design.

### What These ARE

- Format references showing valid syntax
- Field documentation for configuration
- Examples of correct structure

### What These ARE NOT

- Templates to copy verbatim
- Required patterns to follow
- Constraints on creative design

## The Only Constraints

1. **Valid syntax** - YAML must parse, JSON must validate, Markdown must render
2. **Boomerang return** - Sub-agents return to their caller
3. **Requirement fulfillment** - Design must address what's asked

Everything else is creative freedom.

## Response Schema Usage

The `response-schemas.md` file defines structured response formats. Agents SHOULD follow these schemas for:
- Programmatic verification by Orchestrator
- Consistent handoff data
- Clear status communication

Agents MAY return plain markdown if it follows the spirit of the schemas.
