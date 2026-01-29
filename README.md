# audio2mp3

Convert audio files to HQ 320kbps MP3 format with the ease of a Python script.

Requires ffmepg (of course) but supports various input formats and allows for customizable output settings.

## Usage:

```
./audio2mp3.py -h                                                                         
usage: audio2mp3.py [-h] [-o OUTPUT] [--overwrite] [--no-recursive] [--no-structure] input

Convert audio files to 320kbps MP3 format

positional arguments:
  input                Input audio file or directory

options:
  -h, --help           show this help message and exit
  -o, --output OUTPUT  Output file or directory (default: same as input with .mp3 extension)
  --overwrite          Overwrite existing output files
  --no-recursive       Do not process subdirectories (directory mode only)
  --no-structure       Do not preserve directory structure (directory mode only)

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
```
