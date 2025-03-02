import pandas as pd
import re

def identify_verse_boundaries(lyrics):
    """
    Identify verse boundaries using multiple heuristics
    """
    if not isinstance(lyrics, str):
        return []
        
    # Method 1: Split by double newlines (standard verse separator)
    verses = [v for v in lyrics.split('\n\n') if v.strip()]
    
    # If we only got one verse, try more aggressive methods
    if len(verses) <= 1:
        # Method 2: Look for verse indicators
        verse_pattern = re.compile(r'\[(?:Verse|Chorus|Hook|Bridge|Intro|Outro)[\s\d]*\]', re.IGNORECASE)
        matches = list(verse_pattern.finditer(lyrics))
        
        if matches:
            verses = []
            for i in range(len(matches)):
                start = matches[i].end()
                end = matches[i+1].start() if i < len(matches) - 1 else len(lyrics)
                verse = lyrics[start:end].strip()
                if verse:
                    verses.append(verse)
        else:
            # Method 3: Try to split by patterns like multiple consecutive short lines
            lines = lyrics.split('\n')
            verse_breaks = []
            
            for i in range(1, len(lines)-1):
                # If we have a short line between longer ones, it might be a verse break
                if (len(lines[i].strip()) <= 1 and 
                    len(lines[i-1].strip()) > 10 and 
                    len(lines[i+1].strip()) > 10):
                    verse_breaks.append(i)
            
            if verse_breaks:
                verses = []
                last_break = 0
                for brk in verse_breaks:
                    verse = '\n'.join(lines[last_break:brk]).strip()
                    if verse:
                        verses.append(verse)
                    last_break = brk + 1
                
                # Add the last verse
                last_verse = '\n'.join(lines[last_break:]).strip()
                if last_verse:
                    verses.append(last_verse)
    
    # Filter out verses that are too short (likely not actual verses)
    verses = [v for v in verses if len(v.split('\n')) > 1 and len(v) >= 40]
    
    return verses

def main():
    try:
        # Load the dataset
        print("Loading romanized lyrics dataset...")
        try:
            lyrics_df = pd.read_csv('lyrics_romanised.csv')
            print(f"Loaded {len(lyrics_df)} songs")
        except FileNotFoundError:
            print("Error: lyrics_romanised.csv not found. Run romanize.py first.")
            return

        # Remove the 'lyrics' column if it exists
        if 'lyrics' in lyrics_df.columns:
            lyrics_df = lyrics_df.drop(columns=['lyrics'])

        # Split the lyrics into verses
        print("Splitting lyrics into individual verses...")
        lyrics_df['verses'] = lyrics_df['romanized_lyrics'].apply(identify_verse_boundaries)
        
        # Create a new dataframe with artist, title, and individual verses
        print("Creating new dataset with individual verses...")
        new_rows = []
        for _, row in lyrics_df.iterrows():
            for verse in row['verses']:
                new_rows.append({
                    'artist': row['artist'],
                    'title': row['title'],
                    'verse': verse
                })

        # Create the new dataframe
        verse_df = pd.DataFrame(new_rows)
        print(f"Created {len(verse_df)} individual verses from {len(lyrics_df)} songs")
        
        # Filter out very short verses (likely noise)
        original_count = len(verse_df)
        verse_df = verse_df[verse_df['verse'].str.len() > 100]
        print(f"Filtered from {original_count} to {len(verse_df)} verses after removing short verses")
        
        # Save the new dataframe
        output_file = 'lyrics_romanised_split_verses.csv'
        verse_df.to_csv(output_file, index=False)
        print(f"Verse splitting complete. Data saved to {output_file}")

    except Exception as e:
        print(f"Error in verse splitting process: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


