# Hindi Rap Lyrics Generation Project

This repository contains code for curating a Hindi rap lyrics dataset and training a language model to generate new lyrics.

## Dataset Curation Pipeline

The dataset is built through a multi-stage pipeline:

1. **Scraping**: Collecting raw lyrics data from web sources
2. **Preprocessing**: Cleaning and formatting the raw lyrics data
3. **Romanization**: Converting Hindi text to Roman script
4. **Verse Splitting**: Breaking songs into individual verses for better training
5. **Description Generation**: Adding semantic descriptions to verses

### Running the Pipeline

```bash
# Run the entire pipeline
python main.py --steps all

# Run specific steps
python main.py --steps scrape preprocess
```

For description generation (which uses Groq API):
```bash
python main.py --steps describe --groq-key YOUR_API_KEY
```

### Pipeline Details

#### 1. Scraping (`lyrics-scraper.py`)
Collects raw lyrics data and saves as JSON files in the `lyrics` folder.

#### 2. Preprocessing (`preprocess.py`)
- Cleans the raw lyrics data
- Removes duplicates and short lyrics
- Outputs `lyrics.csv`

#### 3. Romanization (`romanize.py`)
- Filters songs to keep only those with Hindi content
- Converts Hindi script to Roman characters
- Outputs `lyrics_romanised.csv`

#### 4. Verse Splitting (`split_verses.py`)
- Breaks songs into individual verses
- Filters out very short verses (less than 100 characters)
- Outputs `lyrics_romanised_split_verses.csv`

#### 5. Description Generation (`lyrics_describe.py`)
- Generates semantic descriptions for each verse
- Processes in batches for efficiency
- Outputs `lyrics_described_final.csv`

## Model Training

The project uses [Unsloth](https://github.com/unslothai/unsloth) to fine-tune a language model on the curated lyrics dataset.

### Prerequisites

```bash
pip install unsloth
```

### Training Process

Training code and hyperparameters can be found in the training notebooks.

## Project Structure

```
├── lyrics/                  # Raw lyrics JSON files
├── README.md                # This file
├── lyrics-scraper.py        # Web scraping script
├── preprocess.py            # Data cleaning and preprocessing
├── romanize.py              # Hindi to Roman script conversion
├── split_verses.py          # Verse splitting script
├── lyrics_describe.py       # Verse description generation
├── main.py                  # Pipeline orchestration
└── training/                # Training notebooks and scripts
```

## Results

The trained model can generate Hindi rap lyrics in the style of the training data.

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`