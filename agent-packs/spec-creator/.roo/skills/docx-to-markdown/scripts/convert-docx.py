#!/usr/bin/env python3
"""
DOCX to Markdown Converter Script
Converts Microsoft Word (.docx) files to Markdown using markitdown CLI.
"""

import sys
import subprocess
import os
from pathlib import Path


def main():
    """Main conversion function."""
    # Check arguments
    if len(sys.argv) < 2:
        print("Error: Missing input file argument", file=sys.stderr)
        print("Usage: python convert-docx.py <input-file.docx> [output-file.md]", file=sys.stderr)
        sys.exit(1)
    
    # Get script directory to resolve relative paths
    script_dir = Path(__file__).parent.parent  # Go up to skill root directory
    
    # Get input file path (relative to skill root)
    input_path_arg = sys.argv[1]
    input_path = (script_dir / input_path_arg).resolve()
    
    # Validate input file
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    if not input_path.suffix.lower() == '.docx':
        print(f"Error: Input file must have .docx extension, got: {input_path.suffix}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output path
    if len(sys.argv) >= 3:
        # Custom output path provided
        output_path_arg = sys.argv[2]
        output_path = (script_dir / output_path_arg).resolve()
    else:
        # Default: same location as input, with .md extension
        output_path = input_path.with_suffix('.md')
    
    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if markitdown is available
    try:
        subprocess.run(
            ['markitdown', '--help'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: markitdown command not found", file=sys.stderr)
        print("Please install it with: pip install 'markitdown[docx]'", file=sys.stderr)
        sys.exit(1)
    
    # Run markitdown conversion
    try:
        print(f"Converting {input_path.name} to Markdown...", file=sys.stderr)
        
        result = subprocess.run(
            ['markitdown', str(input_path), '-o', str(output_path)],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✓ Conversion successful!", file=sys.stderr)
        print(f"✓ Output saved to: {output_path}", file=sys.stderr)
        
        # Return the output path (absolute)
        print(str(output_path))
        sys.exit(0)
        
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        if e.stderr:
            print(f"Details: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
