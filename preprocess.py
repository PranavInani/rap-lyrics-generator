import pandas as pd
import json
import re
import os
from pathlib import Path

def clean_lyrics(text):
    """Clean the raw lyrics text"""
    if not isinstance(text, str):
        return ""
        
    # Remove the first line which usually contains the song title
    text = text.split('\n', 1)[1] if '\n' in text else text
    
    # Remove common patterns in lyrics files
    text = re.sub(r'Embed$', '', text)  # Remove "Embed" at the end
    text = re.sub(r'\[.*?\]', '', text)  # Remove content in square brackets (e.g., [Verse 1])
    text = re.sub(r'\d+EmbedShare URLCopy', '', text)  # Remove sharing info
    text = re.sub(r'See .* LiveGet tickets.*$', '', text, flags=re.MULTILINE)  # Remove concert info
    
    # Fix spacing issues
    text = re.sub(r'\n{3,}', '\n\n', text)  # Replace 3+ newlines with double newlines
    text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)  # Trim each line
    
    return text.strip()

def main():
    lyrics_folder = Path('lyrics')
    output_file = 'lyrics.csv'
    
    print(f"Starting preprocessing of lyrics files in {lyrics_folder}")
    
    # Initialize an empty DataFrame
    df_list = []
    total_files = len([f for f in lyrics_folder.glob('*.json')])
    processed = 0

    # Loop through all files in the lyrics folder
    for filename in lyrics_folder.glob('*.json'):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if 'songs' in data and data['songs']:
                    df_temp = pd.DataFrame(data['songs'])
                    if all(col in df_temp.columns for col in ['title', 'lyrics', 'artist']):
                        # Select only the needed columns
                        df_temp = df_temp[['title', 'lyrics', 'artist']]
                        df_list.append(df_temp)
                    else:
                        print(f"Missing required columns in {filename}")
                else:
                    print(f"No songs found in {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
        
        processed += 1
        if processed % 10 == 0:
            print(f"Processed {processed}/{total_files} files")
    
    # Combine all dataframes
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        print(f"Combined {len(df)} songs from {len(df_list)} files")
        
        # Clean the lyrics
        print("Cleaning lyrics...")
        df['lyrics'] = df['lyrics'].apply(clean_lyrics)
        
        # Remove empty or too short lyrics
        df = df[df['lyrics'].str.len() > 100]
        print(f"Removed short lyrics, {len(df)} songs remaining")
        
        # Remove duplicates
        original_count = len(df)
        df.drop_duplicates(subset=['lyrics'], inplace=True)
        print(f"Removed {original_count - len(df)} duplicate songs")
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"Preprocessing complete. Data saved to {output_file}")
    else:
        print("No valid data found in the lyrics folder")

if __name__ == "__main__":
    main()
