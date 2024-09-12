import os
import subprocess
from pathlib import Path

def mkv_to_mp4(input_file):
    output_file = Path(input_file).with_suffix('.mp4')
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "libx264",
        "-crf", "0",  # Lossless compression
        "-preset", "veryslow",  # Highest compression efficiency
        "-c:a", "copy",  # Copy audio without re-encoding
        str(output_file)
    ]
    
    subprocess.run(ffmpeg_cmd, check=True)

def process_directory(input_dir):
    input_path = Path(input_dir)
    
    for mkv_file in input_path.glob("*.mkv"):
        print(f"Converting {mkv_file}")
        mkv_to_mp4(str(mkv_file))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python mkv_to_mp4.py <input_file.mkv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    mkv_to_mp4(input_file)
