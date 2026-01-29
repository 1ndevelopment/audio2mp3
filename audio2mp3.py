#!/usr/bin/env python3
"""
Audio to 320kbps MP3 Converter
Converts audio files to high-quality 320kbps MP3 format.
Supports individual files and batch conversion of entire directories.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Tuple
import subprocess
import shutil

# Supported input audio formats
SUPPORTED_FORMATS = {
    '.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', 
    '.opus', '.wma', '.aiff', '.ape', '.ac3', '.mp2'
}

class AudioConverter:
    def __init__(self, output_dir: str = None, overwrite: bool = False, keep_structure: bool = True):
        """
        Initialize the audio converter.
        
        Args:
            output_dir: Directory for converted files (None = same as input)
            overwrite: Whether to overwrite existing files
            keep_structure: Keep directory structure when converting folders
        """
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.keep_structure = keep_structure
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if ffmpeg is available."""
        if not shutil.which('ffmpeg'):
            raise RuntimeError(
                "ffmpeg not found. Please install ffmpeg:\n"
                "  Ubuntu/Debian: sudo apt-get install ffmpeg\n"
                "  macOS: brew install ffmpeg\n"
                "  Windows: Download from https://ffmpeg.org/download.html"
            )
    
    def convert_file(self, input_path: Path, output_path: Path = None) -> Tuple[bool, str]:
        """
        Convert a single audio file to 320kbps MP3.
        
        Args:
            input_path: Path to input audio file
            output_path: Path for output file (None = auto-generate)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        input_path = Path(input_path)
        
        # Validate input file
        if not input_path.exists():
            return False, f"Input file not found: {input_path}"
        
        if input_path.suffix.lower() not in SUPPORTED_FORMATS:
            return False, f"Unsupported format: {input_path.suffix}"
        
        # Determine output path
        if output_path is None:
            if self.output_dir:
                output_path = Path(self.output_dir) / f"{input_path.stem}.mp3"
            else:
                output_path = input_path.with_suffix('.mp3')
        else:
            output_path = Path(output_path)
        
        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if output already exists
        if output_path.exists() and not self.overwrite:
            if input_path.suffix.lower() == '.mp3':
                # Check if it's already 320kbps
                bitrate = self._get_bitrate(input_path)
                if bitrate and bitrate >= 320:
                    return False, f"Skipped (already 320kbps): {input_path.name}"
            return False, f"Skipped (file exists): {output_path.name}"
        
        # Build ffmpeg command
        # -i: input file
        # -vn: no video
        # -ar: audio sample rate (44100 Hz)
        # -ac: audio channels (2 for stereo)
        # -b:a: audio bitrate (320k)
        # -y: overwrite output file
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-vn',  # No video
            '-ar', '44100',  # Sample rate
            '-ac', '2',  # Stereo
            '-b:a', '320k',  # Bitrate
            '-map', 'a',  # Map audio stream
            '-map_metadata', '0',  # Copy metadata
            '-id3v2_version', '3',  # ID3v2.3 tags
        ]
        
        if self.overwrite:
            cmd.append('-y')
        
        cmd.append(str(output_path))
        
        try:
            # Run conversion
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                return True, f"Converted: {input_path.name} → {output_path.name}"
            else:
                return False, f"Conversion failed: {input_path.name}\n{result.stderr}"
        
        except Exception as e:
            return False, f"Error converting {input_path.name}: {str(e)}"
    
    def _get_bitrate(self, file_path: Path) -> int:
        """Get the bitrate of an audio file in kbps."""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=bit_rate',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(file_path)
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip()) // 1000  # Convert to kbps
        except:
            pass
        return None
    
    def convert_directory(self, input_dir: Path, recursive: bool = True) -> List[Tuple[bool, str]]:
        """
        Convert all audio files in a directory.
        
        Args:
            input_dir: Path to input directory
            recursive: Whether to process subdirectories
        
        Returns:
            List of (success, message) tuples for each file
        """
        input_dir = Path(input_dir)
        
        if not input_dir.exists():
            return [(False, f"Directory not found: {input_dir}")]
        
        if not input_dir.is_dir():
            return [(False, f"Not a directory: {input_dir}")]
        
        # Find all audio files
        pattern = '**/*' if recursive else '*'
        audio_files = []
        
        for ext in SUPPORTED_FORMATS:
            audio_files.extend(input_dir.glob(f"{pattern}{ext}"))
            audio_files.extend(input_dir.glob(f"{pattern}{ext.upper()}"))
        
        if not audio_files:
            return [(False, f"No audio files found in: {input_dir}")]
        
        # Sort files for consistent processing
        audio_files = sorted(set(audio_files))
        
        results = []
        print(f"\nFound {len(audio_files)} audio file(s) to convert...\n")
        
        for i, audio_file in enumerate(audio_files, 1):
            print(f"[{i}/{len(audio_files)}] Processing: {audio_file.name}")
            
            # Determine output path
            if self.output_dir:
                output_dir = Path(self.output_dir)
                if self.keep_structure and recursive:
                    # Preserve directory structure
                    rel_path = audio_file.relative_to(input_dir)
                    output_path = output_dir / rel_path.with_suffix('.mp3')
                else:
                    output_path = output_dir / f"{audio_file.stem}.mp3"
            else:
                output_path = audio_file.with_suffix('.mp3')
            
            success, message = self.convert_file(audio_file, output_path)
            results.append((success, message))
            print(f"  → {message}")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description='Convert audio files to 320kbps MP3 format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single file
  python audio_converter.py song.flac
  
  # Convert a single file to specific location
  python audio_converter.py song.wav -o output/song.mp3
  
  # Convert all audio files in a directory
  python audio_converter.py /path/to/music/folder
  
  # Convert directory without preserving structure
  python audio_converter.py /path/to/music -o /path/to/output --no-structure
  
  # Convert directory non-recursively
  python audio_converter.py /path/to/music --no-recursive
  
  # Overwrite existing files
  python audio_converter.py music_folder --overwrite
        """
    )
    
    parser.add_argument(
        'input',
        help='Input audio file or directory'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file or directory (default: same as input with .mp3 extension)'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing output files'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not process subdirectories (directory mode only)'
    )
    
    parser.add_argument(
        '--no-structure',
        action='store_true',
        help='Do not preserve directory structure (directory mode only)'
    )
    
    args = parser.parse_args()
    
    # Initialize converter
    converter = AudioConverter(
        output_dir=args.output,
        overwrite=args.overwrite,
        keep_structure=not args.no_structure
    )
    
    input_path = Path(args.input)
    
    # Process input
    if input_path.is_file():
        # Single file conversion
        output_path = Path(args.output) if args.output else None
        success, message = converter.convert_file(input_path, output_path)
        print(message)
        sys.exit(0 if success else 1)
    
    elif input_path.is_dir():
        # Directory conversion
        results = converter.convert_directory(input_path, recursive=not args.no_recursive)
        
        # Print summary
        successful = sum(1 for success, _ in results if success)
        failed = len(results) - successful
        
        print(f"\n{'='*60}")
        print(f"Conversion Summary:")
        print(f"  Total files: {len(results)}")
        print(f"  Successful: {successful}")
        print(f"  Failed/Skipped: {failed}")
        print(f"{'='*60}")
        
        sys.exit(0 if failed == 0 else 1)
    
    else:
        print(f"Error: Input path does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
