#!/usr/bin/env python3
"""
SpotyPod2 - Sync Spotify playlists to Apple Music/iTunes for iPod
"""

import csv
import os
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError


class PlaylistItem:
    """Represents a song in a playlist"""
    
    def __init__(self, track_name: str, artist: str, album: str):
        self.track_name = track_name
        self.artist = artist
        self.album = album
    
    def __repr__(self):
        return f"{self.artist} - {self.track_name}"


class SpotyPod:
    """Main class for syncing Spotify playlists to Apple Music"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def read_exportify_csv(self, csv_path: str) -> tuple[str, List[PlaylistItem]]:
        """
        Read a playlist from an Exportify CSV file
        
        Args:
            csv_path: Path to the Exportify CSV file
            
        Returns:
            Tuple of (playlist_name, list of PlaylistItem objects)
        """
        playlist_items = []
        playlist_name = Path(csv_path).stem
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Exportify CSV format has columns like: Track Name, Artist Name(s), Album Name
                track_name = row.get('Track Name', row.get('track_name', ''))
                artist = row.get('Artist Name(s)', row.get('artist_name', ''))
                album = row.get('Album Name', row.get('album_name', ''))
                
                if track_name and artist:
                    playlist_items.append(PlaylistItem(track_name, artist, album))
        
        return playlist_name, playlist_items
    
    def download_playlist(self, playlist_name: str, playlist_items: List[PlaylistItem]) -> Path:
        """
        Download songs in a playlist using SpotDL
        
        Args:
            playlist_name: Name of the playlist
            playlist_items: List of songs to download
            
        Returns:
            Path to the directory where songs were downloaded
        """
        playlist_dir = self.output_dir / playlist_name
        playlist_dir.mkdir(exist_ok=True)
        
        print(f"\nDownloading playlist: {playlist_name}")
        print(f"Output directory: {playlist_dir}")
        
        # Create a temporary file with search queries for SpotDL
        queries_file = playlist_dir / "queries.txt"
        with open(queries_file, 'w', encoding='utf-8') as f:
            for item in playlist_items:
                # Create search query for SpotDL
                query = f"{item.artist} - {item.track_name}"
                f.write(f"{query}\n")
        
        # Run SpotDL to download the songs
        try:
            cmd = [
                'spotdl',
                'download',
                str(queries_file),
                '--output', str(playlist_dir),
                '--format', 'mp3'
            ]
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"SpotDL stderr: {result.stderr}")
            
            print(f"SpotDL output: {result.stdout}")
        except FileNotFoundError:
            print("Warning: spotdl not found. Please install it with: pip install spotdl")
        
        # Clean up queries file
        queries_file.unlink(missing_ok=True)
        
        return playlist_dir
    
    def get_file_metadata(self, file_path: Path) -> Dict[str, str]:
        """
        Extract metadata from an audio file
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary with metadata (title, artist, album)
        """
        try:
            audio = EasyID3(str(file_path))
            return {
                'title': audio.get('title', [''])[0],
                'artist': audio.get('artist', [''])[0],
                'album': audio.get('album', [''])[0],
            }
        except (ID3NoHeaderError, Exception) as e:
            print(f"Warning: Could not read metadata from {file_path}: {e}")
            return {'title': '', 'artist': '', 'album': ''}
    
    def generate_m3u_playlist(self, playlist_name: str, playlist_dir: Path, 
                              playlist_items: List[PlaylistItem]) -> Path:
        """
        Generate an M3U playlist file with metadata checking and correction
        
        Args:
            playlist_name: Name of the playlist
            playlist_dir: Directory containing downloaded songs
            playlist_items: Original playlist items from CSV
            
        Returns:
            Path to the generated M3U file
        """
        m3u_path = self.output_dir / f"{playlist_name}.m3u"
        
        # Get all MP3 files in the playlist directory
        downloaded_files = list(playlist_dir.glob("*.mp3"))
        
        print(f"\nGenerating M3U playlist: {m3u_path}")
        print(f"Found {len(downloaded_files)} downloaded files")
        print(f"Expected {len(playlist_items)} tracks from CSV")
        
        with open(m3u_path, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            
            # Try to match downloaded files with playlist items
            for item in playlist_items:
                matched_file = None
                
                # Try to find a matching file based on metadata or filename
                for file_path in downloaded_files:
                    metadata = self.get_file_metadata(file_path)
                    
                    # Check if metadata matches
                    title_match = item.track_name.lower() in metadata['title'].lower() or \
                                  metadata['title'].lower() in item.track_name.lower()
                    artist_match = item.artist.lower() in metadata['artist'].lower() or \
                                   metadata['artist'].lower() in item.artist.lower()
                    
                    # Also check filename
                    filename_match = item.track_name.lower() in file_path.stem.lower() and \
                                     item.artist.lower() in file_path.stem.lower()
                    
                    if (title_match and artist_match) or filename_match:
                        matched_file = file_path
                        break
                
                if matched_file:
                    # Get actual metadata from the file
                    metadata = self.get_file_metadata(matched_file)
                    
                    # Write M3U entry with corrected metadata
                    # Use file metadata if available, otherwise use CSV data
                    title = metadata['title'] or item.track_name
                    artist = metadata['artist'] or item.artist
                    
                    # EXTINF format: #EXTINF:duration,artist - title
                    f.write(f"#EXTINF:-1,{artist} - {title}\n")
                    f.write(f"{matched_file.absolute()}\n")
                    
                    # Check for mismatches
                    if metadata['title'] and metadata['title'].lower() != item.track_name.lower():
                        print(f"  Metadata mismatch - CSV: '{item.track_name}' vs File: '{metadata['title']}'")
                    if metadata['artist'] and metadata['artist'].lower() != item.artist.lower():
                        print(f"  Artist mismatch - CSV: '{item.artist}' vs File: '{metadata['artist']}'")
                else:
                    print(f"  Warning: Could not find downloaded file for: {item}")
        
        print(f"M3U playlist saved to: {m3u_path}")
        return m3u_path
    
    def process_playlist(self, csv_path: str, download: bool = True) -> Path:
        """
        Complete workflow: read CSV, download songs, generate M3U
        
        Args:
            csv_path: Path to Exportify CSV file
            download: Whether to download songs (set to False to only generate M3U from existing files)
            
        Returns:
            Path to the generated M3U file
        """
        print(f"Processing playlist from: {csv_path}")
        
        # Read the playlist from CSV
        playlist_name, playlist_items = self.read_exportify_csv(csv_path)
        print(f"Loaded playlist '{playlist_name}' with {len(playlist_items)} tracks")
        
        # Download songs if requested
        if download:
            playlist_dir = self.download_playlist(playlist_name, playlist_items)
        else:
            playlist_dir = self.output_dir / playlist_name
            if not playlist_dir.exists():
                raise ValueError(f"Playlist directory not found: {playlist_dir}")
        
        # Generate M3U playlist with metadata checking
        m3u_path = self.generate_m3u_playlist(playlist_name, playlist_dir, playlist_items)
        
        return m3u_path


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='SpotyPod2 - Sync Spotify playlists to Apple Music for iPod',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single playlist (download and create M3U)
  python spotypod.py playlist.csv
  
  # Process playlist without downloading (if songs already downloaded)
  python spotypod.py playlist.csv --no-download
  
  # Specify custom output directory
  python spotypod.py playlist.csv --output my_playlists
        """
    )
    
    parser.add_argument('csv_file', help='Path to Exportify CSV file')
    parser.add_argument('--output', '-o', default='output',
                        help='Output directory (default: output)')
    parser.add_argument('--no-download', action='store_true',
                        help='Skip downloading, only generate M3U from existing files')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file not found: {args.csv_file}")
        return 1
    
    spotypod = SpotyPod(output_dir=args.output)
    
    try:
        m3u_path = spotypod.process_playlist(args.csv_file, download=not args.no_download)
        print(f"\n✓ Success! M3U playlist created: {m3u_path}")
        print(f"\nYou can now import '{m3u_path}' into Apple Music/iTunes")
        return 0
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
