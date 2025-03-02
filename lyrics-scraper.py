import lyricsgenius
import os
import time
import json
from pathlib import Path

# Create a lyrics directory if it doesn't exist
lyrics_dir = Path('lyrics')
lyrics_dir.mkdir(exist_ok=True)

# Initialize Genius API client with your token 
# (consider using environment variables for API keys in production)
genius = lyricsgenius.Genius("wBaaP7NG7DSQgkPaRGBa5ghsJxYeHneH89V4WnJZXCi_mOQDNZBnOpGkITtwjvfe", 
                             skip_non_songs=True, 
                             remove_section_headers=True,
                             timeout=15,
                             retries=3)

# Comprehensive list of Hindi/Indian rap artists
artists = [
    "Divine", "Raftaar", "Badshah", "Emiway Bantai", "Naezy",
    "Seedhe Maut", "Prabh Deep", "Ikka", "Raga", "Karma",
    "MC Stan", "Kaam Bhaari", "Dino James", "Kr$na", "EPR",
    "Fotty Seven", "Talha Anjum", "Muhfaad", "Yashraj", "YungSta",
    "MC Altaf", "Panther", "Young Stunners", "Rap Demon", "MZee Bella"
]

# Track the progress
total_artists = len(artists)
completed = 0
failed = []

for artist_name in artists:
    try:
        print(f"Scraping lyrics for {artist_name} ({completed+1}/{total_artists})...")
        
        # Check if we already have this artist's lyrics
        artist_file = lyrics_dir / f"Lyrics_{artist_name.replace(' ', '_')}.json"
        if artist_file.exists():
            print(f"Lyrics for {artist_name} already exists. Skipping.")
            completed += 1
            continue
            
        # Get artist and songs (max 50 songs per artist to avoid very large files)
        artist = genius.search_artist(artist_name, max_songs=50, sort="popularity")
        
        if artist and artist.songs:
            artist.save_lyrics(filename=f'lyrics/Lyrics_{artist_name.replace(" ", "_")}')
            print(f"Successfully saved lyrics for {artist_name}")
        else:
            print(f"No songs found for {artist_name}")
            failed.append(artist_name)
            
        # Respect API rate limits with a delay
        time.sleep(5)
        
    except Exception as e:
        print(f"Error scraping {artist_name}: {str(e)}")
        failed.append(artist_name)
        time.sleep(10)  # Longer delay after an error
        
    completed += 1

# Print summary
print(f"\nScraping completed: {completed-len(failed)}/{total_artists} artists successful")
if failed:
    print(f"Failed artists: {', '.join(failed)}")
