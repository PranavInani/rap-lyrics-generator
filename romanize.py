import pandas as pd
import re
import time
import sys

def main():
    try:
        # Check if AI4Bharat transliteration engine is installed
        try:
            from ai4bharat.transliteration import XlitEngine
            e = XlitEngine(beam_width=4, rescore=False, src_script_type="indic")
            transliteration_available = True
            print("Transliteration engine loaded successfully")
        except ImportError:
            print("Warning: ai4bharat transliteration package not found.")
            print("To install: pip install ai4bharat-transliteration")
            print("Proceeding without transliteration capability")
            transliteration_available = False

        # Load the dataset
        print("Loading lyrics dataset...")
        try:
            df = pd.read_csv("lyrics.csv")
            print(f"Loaded {len(df)} songs from lyrics.csv")
        except FileNotFoundError:
            print("Error: lyrics.csv not found. Run preprocess.py first.")
            return
            
        # Helper function to check if a word is in Hindi script
        def is_hindi(word):
            # Unicode range for Devanagari script (Hindi characters)
            return bool(re.search(r'[\u0900-\u097F]', word))

        # Function to transliterate Hindi words in a sentence
        def transliterate_sentence(sentence):
            if not transliteration_available:
                return sentence
                
            if not isinstance(sentence, str):
                return ""
                
            lines = sentence.split('\n')
            transliterated_lines = []

            for line in lines:
                words = re.split(r'([ -])', line)  # Split but keep separators
                transliterated_parts = []

                i = 0
                while i < len(words):
                    word = words[i]
                    if not word.strip():  # Handle empty parts
                        transliterated_parts.append(word)
                    elif is_hindi(word):  # Check if the word is Hindi
                        try:
                            transliterated_word = e.translit_word(word, 'hi', topk=1)[0]
                            transliterated_parts.append(transliterated_word)
                        except Exception:
                            transliterated_parts.append(word)  # Keep original if transliteration fails
                    else:
                        transliterated_parts.append(word)  # Keep non-Hindi words as they are
                    
                    i += 1
                
                transliterated_lines.append("".join(transliterated_parts))
            
            return "\n".join(transliterated_lines)

        # Function to check if text contains Hindi content
        def contains_hindi(text):
            if not isinstance(text, str):
                return False
            # Check if at least 5% of words have Hindi characters
            words = text.split()
            if not words:
                return False
                
            hindi_words = sum(1 for word in words if is_hindi(word))
            return (hindi_words / len(words)) >= 0.05

        # Filter to keep only texts with Hindi content
        print("Filtering songs containing Hindi content...")
        original_count = len(df)
        df = df[df['lyrics'].apply(contains_hindi)]
        print(f"Filtered from {original_count} to {len(df)} songs with Hindi content")

        # Create a new column for romanized lyrics
        print("Romanizing lyrics (this may take a while)...")
        if transliteration_available:
            df['romanized_lyrics'] = df['lyrics'].apply(transliterate_sentence)
        else:
            # If transliteration is not available, just copy the original lyrics
            df['romanized_lyrics'] = df['lyrics']
            print("Skipped transliteration due to missing package")

        # Save the romanized dataset
        output_file = 'lyrics_romanised.csv'
        df.to_csv(output_file, index=False)
        print(f"Romanization complete. Data saved to {output_file}")

    except Exception as e:
        print(f"Error in romanization process: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
