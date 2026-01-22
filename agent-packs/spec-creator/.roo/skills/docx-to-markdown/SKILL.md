---
name: docx-to-markdown
description: Convert Microsoft Word (.docx) files to Markdown format using the markitdown CLI tool. Use this skill when you need to extract text content from Word documents, make docx files readable by LLMs, or convert Word documents to Markdown for text processing pipelines.
compatibility: Requires Python 3.10+ and markitdown package with docx support (pip install 'markitdown[docx]')
metadata:
  author: agentskills
  version: "1.0"
---

# DOCX to Markdown Conversion

This skill converts Microsoft Word (.docx) files to Markdown format using the markitdown CLI tool.

## Prerequisites

Before using this skill, ensure:
- Python 3.10 or higher is installed
- The `markitdown` package with docx support is installed: `pip install 'markitdown[docx]'`

## Usage Instructions

### Basic Conversion

To convert a docx file to markdown:

1. Use the conversion script with the path to the docx file (relative to this skill's location):
   ```bash
   python scripts/convert-docx.py <path-to-docx-file>
   ```

2. The script will:
   - Validate the input file exists and has a `.docx` extension
   - Convert the file to Markdown using markitdown
   - Save the output as a `.md` file in the same directory as the source file
   - Return the path to the generated Markdown file

### Custom Output Location

To specify a custom output location:

```bash
python scripts/convert-docx.py <path-to-docx-file> <path-to-output-file.md>
```

## Examples

### Example 1: Convert a docx file in the same directory
```bash
python scripts/convert-docx.py document.docx
```
Output: `document.md` (in the same directory as `document.docx`)

### Example 2: Convert a docx file in a subdirectory
```bash
python scripts/convert-docx.py ../../docs/report.docx
```
Output: `../../docs/report.md`

### Example 3: Specify custom output location
```bash
python scripts/convert-docx.py document.docx output/converted.md
```
Output: `output/converted.md`

## Important Notes

- All paths should be specified relative to the location of this SKILL.md file
- The script will create any necessary parent directories for the output file
- If the output file already exists, it will be overwritten
- The source docx file is not modified or deleted

## Error Handling

The script will display helpful error messages for common issues:
- File not found
- Invalid file extension (must be .docx)
- Missing markitdown package
- Conversion errors

## Return Value

Upon successful conversion, the script returns the absolute path to the generated Markdown file.
