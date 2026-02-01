# SpotyPod2 Usage Examples

This guide provides practical examples for using SpotyPod2.

## Quick Start Example

### 1. Export Your Spotify Playlist

1. Go to [Exportify](https://exportify.net/)
2. Log in with Spotify
3. Find your playlist (e.g., "Road Trip Mix")
4. Click "Export" and save as `road_trip_mix.csv`

### 2. Download and Convert

```bash
# Basic usage - download and create M3U
python spotypod.py road_trip_mix.csv
```

**Output:**
```
Processing playlist from: road_trip_mix.csv
Loaded playlist 'road_trip_mix' with 25 tracks

Downloading playlist: road_trip_mix
Output directory: output/road_trip_mix
Running: spotdl download ...
[SpotDL downloads songs...]

Generating M3U playlist: output/road_trip_mix.m3u
Found 25 downloaded files
Expected 25 tracks from CSV
M3U playlist saved to: output/road_trip_mix.m3u

✓ Success! M3U playlist created: output/road_trip_mix.m3u
```

### 3. Import to Apple Music

1. Open Apple Music/iTunes
2. File → Library → Import Playlist
3. Select `output/road_trip_mix.m3u`
4. Playlist appears in your library
5. Sync to your iPod

## Advanced Examples

### Custom Output Location

Keep playlists organized in a specific directory:

```bash
python spotypod.py my_playlist.csv --output ~/Music/iPod_Playlists
```

### Regenerate M3U Without Re-downloading

Already downloaded the songs? Just regenerate the M3U:

```bash
python spotypod.py my_playlist.csv --no-download
```

This is useful if:
- You manually edited some files
- You want to update metadata
- SpotDL downloaded with different names

### Processing Multiple Playlists

Create a simple script to process multiple playlists:

```bash
#!/bin/bash
for playlist in *.csv; do
    echo "Processing $playlist..."
    python spotypod.py "$playlist"
done
```

## Understanding the Output

### Directory Structure

After running SpotyPod2:

```
output/
├── my_playlist/
│   ├── Artist1 - Song1.mp3
│   ├── Artist2 - Song2.mp3
│   └── ...
└── my_playlist.m3u
```

### M3U File Format

The generated `.m3u` file looks like:

```
#EXTM3U
#EXTINF:-1,Artist Name - Song Title
/full/path/to/output/my_playlist/Artist - Song.mp3
#EXTINF:-1,Another Artist - Another Song
/full/path/to/output/my_playlist/Another Artist - Another Song.mp3
```

### Console Output Example

When processing a playlist, you'll see output like this:

```
Processing playlist from: my_playlist.csv
Loaded playlist 'my_playlist' with 3 tracks

Generating M3U playlist: output/my_playlist.m3u
Found 3 downloaded files
Expected 3 tracks from CSV

Checking metadata and correcting playlist entries...
  ⚠ Metadata mismatch detected:
    CSV Expected: 'Bohemian Rhapsody'
    File Contains: 'Bohemian Rhapsody (Remastered 2011)'
    → M3U will use: 'Bohemian Rhapsody (Remastered 2011)' (from file)

============================================================
M3U Playlist Generation Summary:
  ✓ Matched correctly: 2 tracks
  ⚠ Corrected mismatches: 1 track
  ✗ Missing files: 0 tracks
  Total in playlist: 3 tracks
============================================================

Note: 1 track had metadata mismatches.
The M3U playlist has been corrected to use the actual file metadata
to ensure proper recognition when imported into Apple Music/iTunes.
```

This clearly shows:
- Which tracks matched perfectly
- Which tracks had metadata differences
- What corrections were applied
- The final M3U uses the **actual file metadata** for proper Apple Music recognition

## Common Scenarios

### Metadata Mismatches

**Problem:** SpotDL found a different version of the song

**Example Output:**
```
⚠ Metadata mismatch detected:
  CSV Expected: 'Song Title'
  File Contains: 'Song Title (Remastered)'
  → M3U will use: 'Song Title (Remastered)' (from file)
```

**What This Means:**
- Your Exportify CSV listed "Song Title"
- SpotDL downloaded "Song Title (Remastered)" instead
- The M3U playlist has been **automatically corrected** to use the actual file metadata

**Why It's Corrected:**
When you import the M3U into Apple Music/iTunes, it needs to match the actual song files. If the M3U said "Song Title" but the file contains "Song Title (Remastered)", Apple Music wouldn't recognize the song. By correcting the M3U to match the file, everything imports smoothly.

**What You Should Do:**
- Review the mismatches to ensure you got the right songs
- The playlist will work correctly in Apple Music/iTunes because it matches the actual files
- If you got the wrong song, delete it, manually download the correct one, and re-run with `--no-download`

### Missing Songs

**Problem:** Some songs couldn't be downloaded

**What happens:**
- SpotDL may not find some songs on YouTube
- The M3U will only include songs that were successfully downloaded

**Solution:**
- Check SpotDL output for errors
- Manually search for missing songs
- Add them to the playlist folder
- Re-run with `--no-download` to update the M3U

### Different Spotify Account Playlists

**Problem:** Want to sync playlists from multiple accounts

**Solution:** Just export from each account and process separately:

```bash
python spotypod.py account1_playlist.csv --output account1_music
python spotypod.py account2_playlist.csv --output account2_music
```

## Tips & Best Practices

### 1. Test with Small Playlists First

Start with a small playlist (5-10 songs) to ensure everything works:

```bash
# Create a test playlist with just a few songs
python spotypod.py test_playlist.csv
```

### 2. Check Downloaded Quality

SpotDL downloads from YouTube. Quality may vary:
- Most songs: 128-320 kbps MP3
- Check SpotDL options for quality settings
- Consider using `--bitrate 320k` with SpotDL

### 3. Organize by Genre or Purpose

```bash
python spotypod.py workout.csv --output ~/Music/Workout
python spotypod.py relaxing.csv --output ~/Music/Relaxing
python spotypod.py party.csv --output ~/Music/Party
```

### 4. Backup Your Playlists

The CSV files are small - keep backups:

```bash
mkdir playlist_backups
cp *.csv playlist_backups/
```

### 5. Update Playlists Periodically

As your Spotify playlists change:

1. Re-export from Exportify
2. Run SpotyPod2 again
3. New songs will be downloaded
4. M3U will be updated

## Troubleshooting Examples

### Check What SpotDL Downloaded

```bash
ls -lh output/my_playlist/
```

### Verify MP3 Metadata

```bash
# Install ffprobe (part of ffmpeg)
ffprobe "output/my_playlist/Song.mp3"
```

### Re-download Single Songs

If a specific song failed:

```bash
# Download manually with SpotDL
spotdl download "Artist - Song Name" --output output/my_playlist/
```

Then regenerate the M3U:

```bash
python spotypod.py my_playlist.csv --no-download
```

## Integration with iTunes/Apple Music

### Creating Smart Playlists

After importing the M3U:

1. In Apple Music, right-click the playlist
2. Select "Edit Smart Playlist"
3. Add rules to automatically include new songs

### Syncing to iPod

1. Connect iPod to computer
2. Open Apple Music/iTunes
3. Select your iPod from sidebar
4. Check the playlists you want to sync
5. Click "Sync" or "Apply"

### Converting to Different Format

If your iPod needs a different format:

1. In iTunes, select all songs in the playlist
2. File → Convert → Create AAC Version (or MP3)
3. Create new playlist with converted songs
