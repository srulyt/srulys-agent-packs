---
name: vtt-reducer
description: Reduces verbose WebVTT transcript files into clean, consolidated Markdown format for use in agentic workflows. Use when working with VTT meeting transcripts that need to be processed, summarized, or used as context for document creation.
compatibility: Requires Python 3.6+
metadata:
  author: fabric-team
  version: "1.0"
---

# VTT Transcript Reducer

This skill converts verbose WebVTT transcript files into clean, consolidated Markdown format suitable for use as context in agentic processes.

## When to Use

Use this skill when:
- You have a WebVTT (.vtt) transcript file from a meeting recording
- The transcript needs to be used as input for document creation or updates
- You need a clean, readable version of the conversation without technical VTT metadata
- The file is too large or verbose to use directly in LLM context windows

## What It Does

The skill processes VTT files to:
1. **Remove redundant metadata**: Strips cue identifiers, eliminates unnecessary markup
2. **Consolidate speakers**: Merges consecutive entries from the same speaker into single blocks
3. **Preserve timestamps**: Includes timestamps at speaker changes for temporal reference
4. **Output clean Markdown**: Generates a readable format optimized for agentic processing

## Input/Output

**Input**: WebVTT (.vtt) transcript file with speaker voice tags
**Output**: Markdown (.md) file with consolidated speaker dialogue and timestamps

## How to Use

### Basic Usage

To reduce a VTT file in the same directory:

```bash
python scripts/vtt-reducer.py <path-to-file.vtt>
```

The reduced transcript will be saved to `<filename>_reduced.md` in the same directory as the input file.

### Custom Output Path

To specify a custom output location:

```bash
python scripts/vtt-reducer.py <path-to-file.vtt> <output-path.md>
```

### Example

```bash
# Reduce a meeting transcript from the workspace root
python scripts/vtt-reducer.py ../../.context/transcript.vtt

# Output will be saved to: ../../.context/transcript_reduced.md
```

**Note**: All paths in the examples above are relative to the skill directory. When executing from the workspace root, use the full path: `python {skills-location}/vtt-reducer/scripts/vtt-reducer.py <path>`.

## Output Format

The reduced transcript uses this format:

```markdown
# Meeting Transcript

**[00:00:03] Speaker Name:** Full consolidated text from this speaker including all consecutive entries merged together...

**[00:05:42] Another Speaker:** Their consolidated dialogue...

**[00:08:15] Speaker Name:** Continuing the conversation...
```

## Skill Workflow

When using this skill:

1. **Execute the parser script** using the command above with the VTT file path
2. **Wait for completion** - the script will display progress and output location
3. **Use the reduced file** - the `_reduced.md` file is now ready for use in other agentic tasks
4. **Return the file path** to the user for further processing

## Important Notes

- **Do not read the VTT file content** - it may be very large. Execute the script directly.
- The script handles file reading and parsing efficiently
- Timestamps are preserved at each speaker change to maintain temporal context
- All VTT markup and cue identifiers are removed for clean output
- The output is optimized for LLM consumption with minimal tokens

## Error Handling

The script validates:
- Input file exists
- VTT format is valid
- Output directory is writable

Common errors and solutions:
- **File not found**: Check the file path is correct relative to current directory
- **Permission denied**: Ensure write permissions in the output directory
- **Invalid VTT format**: Verify the file is a valid WebVTT transcript with speaker voice tags

## Technical Details

The parser:
- Uses regex to extract timestamps, speakers, and text from VTT cues
- Consolidates consecutive speaker entries to reduce redundancy
- Preserves chronological order
- Handles speaker name variations consistently
- Outputs UTF-8 encoded Markdown for universal compatibility
