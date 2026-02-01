# SpotyPod2

Program to help sync Spotify playlists to Apple Music/iTunes for iPod syncing.

## Overview

SpotyPod2 automates the process of:
1. Reading Spotify playlists exported via Exportify (CSV format)
2. Downloading songs using SpotDL
3. Organizing downloads into playlist-specific folders
4. Checking metadata mismatches between CSV and downloaded files
5. Generating M3U playlists with corrected metadata for Apple Music/iTunes import

## Prerequisites

- Python 3.7 or higher (tested with Python 3.9+)
- [Exportify](https://exportify.net/) - to export Spotify playlists to CSV
- [SpotDL](https://github.com/spotDL/spotify-downloader) - for downloading songs
- Apple Music or iTunes - for importing playlists to sync to iPod

## Installation

1. Clone this repository:
```bash
git clone https://github.com/othuertas/SpotyPod2.git
cd SpotyPod2
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install SpotDL (if not already installed):
```bash
pip install spotdl
```

## Usage

For detailed examples and use cases, see [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md).

### Step 1: Export Spotify Playlist

1. Go to [Exportify](https://exportify.net/)
2. Log in with your Spotify account
3. Click "Export" on the playlist you want to sync
4. Save the CSV file (e.g., `my_playlist.csv`)

### Step 2: Process Playlist with SpotyPod2

Basic usage:
```bash
python spotypod.py my_playlist.csv
```

This will:
- Download all songs from the playlist to `output/my_playlist/`
- Generate an M3U playlist file at `output/my_playlist.m3u`
- Report any metadata mismatches found

### Advanced Options

Specify custom output directory:
```bash
python spotypod.py my_playlist.csv --output my_playlists
```

Skip downloading (if songs already downloaded):
```bash
python spotypod.py my_playlist.csv --no-download
```

View all options:
```bash
python spotypod.py --help
```

### Step 3: Import to Apple Music/iTunes

1. Open Apple Music or iTunes
2. Go to File → Library → Import Playlist
3. Select the generated `.m3u` file
4. The playlist will be imported and ready to sync to your iPod

## How It Works

### CSV Parsing
The program reads Exportify CSV files which contain playlist metadata including:
- Track Name
- Artist Name(s)
- Album Name

### Downloading
Songs are downloaded using SpotDL into separate folders for each playlist:
```
output/
  playlist_name/
    song1.mp3
    song2.mp3
    ...
  playlist_name.m3u
```

### Metadata Checking
The program compares the metadata in:
- The Exportify CSV (what you intended to download)
- The actual downloaded MP3 files (what was actually downloaded)

Any mismatches are reported so you can verify the downloads are correct.

### M3U Generation
An M3U playlist file is created with:
- Corrected metadata based on actual downloaded files
- Absolute file paths for Apple Music/iTunes compatibility
- Extended M3U format with track information

## Troubleshooting

### SpotDL not found
Make sure SpotDL is installed and in your PATH:
```bash
pip install spotdl
```

### Metadata mismatches
The program will report mismatches between the CSV and downloaded files. This can happen when:
- SpotDL found a different version of the song
- The song has been re-released or remastered
- Artist name formatting differs

Review the mismatches and manually verify if needed.

### Songs not downloading
- Check your internet connection
- Some songs may not be available on YouTube (SpotDL's source)
- SpotDL may require updates: `pip install --upgrade spotdl`

## Configuration

Copy `config.ini.example` to `config.ini` to customize settings:
```bash
cp config.ini.example config.ini
```

Edit `config.ini` to set default output directory and other options.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is provided as-is for personal use.
