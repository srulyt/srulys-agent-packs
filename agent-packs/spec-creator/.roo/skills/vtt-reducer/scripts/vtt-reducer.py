#!/usr/bin/env python3
"""
VTT Transcript Reducer
Converts verbose WebVTT transcript files into clean, consolidated Markdown format.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional


class VTTReducer:
    def __init__(self, input_path: str, output_path: Optional[str] = None):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path) if output_path else self._get_default_output_path()
        
    def _get_default_output_path(self) -> Path:
        """Generate default output path with _reduced.md suffix."""
        return self.input_path.parent / f"{self.input_path.stem}_reduced.md"
    
    def parse_vtt(self) -> List[Tuple[str, str, str]]:
        """
        Parse VTT file and extract cues with timestamps and speaker text.
        Returns list of (timestamp, speaker, text) tuples.
        """
        cues = []
        
        with open(self.input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by double newlines to get individual cues
        blocks = content.split('\n\n')
        
        for block in blocks:
            if not block.strip() or block.strip() == 'WEBVTT':
                continue
            
            lines = block.strip().split('\n')
            
            # Skip if not enough lines for a valid cue
            if len(lines) < 2:
                continue
            
            # Extract timestamp (second line in a cue block)
            timestamp_line = None
            text_lines = []
            
            for i, line in enumerate(lines):
                if '-->' in line:
                    timestamp_line = line
                    # Everything after timestamp is text
                    text_lines = lines[i+1:]
                    break
            
            if not timestamp_line or not text_lines:
                continue
            
            # Parse timestamp (get start time)
            timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3})', timestamp_line)
            if not timestamp_match:
                continue
            
            timestamp = timestamp_match.group(1)
            
            # Extract speaker and text from voice tags
            full_text = ' '.join(text_lines)
            
            # Match <v Speaker Name>text</v> pattern
            voice_match = re.search(r'<v\s+([^>]+)>(.+?)</v>', full_text)
            
            if voice_match:
                speaker = voice_match.group(1).strip()
                text = voice_match.group(2).strip()
                cues.append((timestamp, speaker, text))
        
        return cues
    
    def consolidate_speakers(self, cues: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
        """
        Consolidate consecutive entries from the same speaker.
        Returns list of (timestamp, speaker, consolidated_text) tuples.
        """
        if not cues:
            return []
        
        consolidated = []
        current_timestamp, current_speaker, current_text = cues[0]
        
        for timestamp, speaker, text in cues[1:]:
            if speaker == current_speaker:
                # Same speaker - append text
                current_text += ' ' + text
            else:
                # Different speaker - save current and start new
                consolidated.append((current_timestamp, current_speaker, current_text))
                current_timestamp = timestamp
                current_speaker = speaker
                current_text = text
        
        # Don't forget the last entry
        consolidated.append((current_timestamp, current_speaker, current_text))
        
        return consolidated
    
    def format_timestamp(self, timestamp: str) -> str:
        """Convert HH:MM:SS.mmm to [HH:MM:SS] format."""
        # Remove milliseconds
        return f"[{timestamp.split('.')[0]}]"
    
    def generate_markdown(self, consolidated_cues: List[Tuple[str, str, str]]) -> str:
        """Generate clean Markdown output from consolidated cues."""
        lines = ["# Meeting Transcript\n"]
        
        for timestamp, speaker, text in consolidated_cues:
            formatted_time = self.format_timestamp(timestamp)
            lines.append(f"**{formatted_time} {speaker}:** {text}\n")
        
        return '\n'.join(lines)
    
    def reduce(self) -> str:
        """Main method to reduce VTT file and save output."""
        print(f"Reading VTT file: {self.input_path}")
        
        # Parse VTT
        cues = self.parse_vtt()
        print(f"Parsed {len(cues)} cues")
        
        # Consolidate consecutive entries from same speaker
        consolidated = self.consolidate_speakers(cues)
        print(f"Consolidated to {len(consolidated)} speaker entries")
        
        # Generate markdown
        markdown = self.generate_markdown(consolidated)
        
        # Write output
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"Reduced transcript saved to: {self.output_path}")
        
        return str(self.output_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python vtt-reducer.py <input.vtt> [output.md]")
        print("  If output path is not specified, will use <input>_reduced.md")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(input_path).exists():
        print(f"Error: Input file '{input_path}' not found")
        sys.exit(1)
    
    try:
        reducer = VTTReducer(input_path, output_path)
        output_file = reducer.reduce()
        print(f"\n✓ Success! Reduced transcript: {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
