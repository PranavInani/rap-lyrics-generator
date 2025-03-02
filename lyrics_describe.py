import time
import pandas as pd
import os
from pathlib import Path
import argparse

def main():
    try:
        # Set up argument parser for flexibility
        parser = argparse.ArgumentParser(description='Generate reverse prompts for rap verses using Groq API')
        parser.add_argument('--batch-size', type=int, default=50, help='Number of verses to process in each batch')
        parser.add_argument('--output-dir', type=str, default='batches', help='Directory to save batch results')
        parser.add_argument('--api-key', type=str, help='Groq API key (optional if set as env variable)')
        args = parser.parse_args()
        
        # Create output directory if it doesn't exist
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Load the dataset
        print("Loading verse dataset...")
        try:
            df = pd.read_csv("lyrics_romanised_split_verses.csv")
            print(f"Loaded {len(df)} verses")
        except FileNotFoundError:
            print("Error: lyrics_romanised_split_verses.csv not found. Run split_verses.py first.")
            return
            
        # Import Groq dynamically to handle when it's not installed
        try:
            from groq import Groq
            # Initialize Groq client - first try argument, then environment variable
            api_key = args.api_key or os.environ.get("GROQ_API_KEY")
            if not api_key:
                print("Error: Groq API key not provided. Use --api-key or set GROQ_API_KEY environment variable.")
                return
                
            client = Groq(api_key=api_key)
            print("Groq client initialized")
            
        except ImportError:
            print("Error: Groq package not installed. Run 'pip install groq' first.")
            return
            
        # Function to generate reverse prompts for a verse
        def generate_reverse_prompt(index, verse, max_tokens=300):
            print(f"Processing verse {index}...")
            try:
                # Format the input with artist and title context if available
                artist_info = f"Artist: {df.at[index, 'artist']}" if 'artist' in df.columns else ""
                title_info = f"Title: {df.at[index, 'title']}" if 'title' in df.columns else ""
                context = f"{artist_info} {title_info}".strip()
                
                prompt = f"""Analyze the following Hinglish rap verse and create a reverse prompt that captures its theme, tone, style, and key elements. 
The reverse prompt should guide a language model to generate a similar verse. 
Be specific about the tone, rhyming style, and any cultural or stylistic features.

{context}

Verse: "{verse}"

Write a concise reverse prompt:"""

                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=max_tokens,
                    top_p=1,
                    stream=True,
                    stop=None,
                )
                
                reverse_prompt = ""
                for chunk in completion:
                    reverse_prompt += chunk.choices[0].delta.content or ""
                
                return reverse_prompt
            except Exception as e:
                print(f"Error generating reverse prompt for index {index}: {str(e)}")
                return f"Error: {str(e)}"

        # Function to process a batch
        def process_batch(batch_df, batch_number):
            batch_file_name = output_dir / f"lyrics_described_batch_{batch_number}.csv"
            
            # Check if the batch file already exists
            if batch_file_name.exists():
                print(f"Batch {batch_number} already processed. Skipping.")
                return batch_file_name
                
            print(f"Processing batch {batch_number} with {len(batch_df)} verses...")
            
            # Generate reverse prompts for each verse in the batch
            batch_df['reverse_prompt'] = batch_df.apply(
                lambda row: generate_reverse_prompt(row.name, row['verse']), 
                axis=1
            )
            
            # Save the batch results
            batch_df.to_csv(batch_file_name, index=False)
            print(f"Batch {batch_number} processed and saved to {batch_file_name}")
            
            # Sleep between batches to avoid rate limiting
            print(f"Waiting 30 seconds before next batch...")
            time.sleep(30)
            
            return batch_file_name

        # Process the dataset in batches
        batch_size = args.batch_size
        total_rows = len(df)
        batch_files = []
        
        for batch_idx, start_idx in enumerate(range(0, total_rows, batch_size)):
            end_idx = min(start_idx + batch_size, total_rows)
            batch_df = df.iloc[start_idx:end_idx].copy()
            batch_number = batch_idx + 1
            
            batch_file = process_batch(batch_df, batch_number)
            if batch_file:
                batch_files.append(batch_file)
            
        # Combine all batches into a final dataset
        if batch_files:
            print("\nAll batches processed. Combining results...")
            final_df = pd.concat([pd.read_csv(file) for file in batch_files], ignore_index=True)
            final_df.to_csv("lyrics_described_final.csv", index=False)
            print("Final dataset saved as 'lyrics_described_final.csv'")
        else:
            print("No batches were processed.")

    except Exception as e:
        print(f"Error in description process: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()