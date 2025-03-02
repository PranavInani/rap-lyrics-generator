#!/usr/bin/env python3
import subprocess
import argparse
import sys
import os
from pathlib import Path

def run_step(step_name, script_path, args=None):
    """Run a step in the pipeline and check for success"""
    print(f"\n{'='*80}")
    print(f"RUNNING STEP: {step_name}")
    print(f"{'='*80}\n")
    
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
        
    try:
        process = subprocess.run(cmd, check=True)
        if process.returncode == 0:
            print(f"\n✅ {step_name} completed successfully")
            return True
        else:
            print(f"\n❌ {step_name} failed with return code {process.returncode}")
            return False
    except subprocess.SubprocessError as e:
        print(f"\n❌ {step_name} failed with error: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ {step_name} failed unexpectedly: {str(e)}")
        return False

def check_requirements():
    """Check if required packages are installed"""
    requirements = ['pandas', 'lyricsgenius']
    missing = []
    
    for req in requirements:
        try:
            __import__(req)
        except ImportError:
            missing.append(req)
    
    if missing:
        print("Missing required packages. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing)
        print("Installation complete.")
    
    # Check for optional packages
    optional = {
        'ai4bharat-transliteration': 'Transliteration capabilities',
        'groq': 'Verse description capabilities'
    }
    
    for pkg, desc in optional.items():
        try:
            __import__(pkg.replace('-', '_'))  # Replace hyphen for import
            print(f"✅ {pkg} is installed ({desc})")
        except ImportError:
            print(f"⚠️ {pkg} is not installed. {desc} will be limited.")
            print(f"  To install: pip install {pkg}")

def main():
    parser = argparse.ArgumentParser(description='Run the rap lyrics dataset generation pipeline')
    parser.add_argument('--steps', type=str, nargs='+', choices=['scrape', 'preprocess', 'romanize', 'split', 'describe', 'all'], 
                        default=['all'], help='Specific steps to run')
    parser.add_argument('--groq-key', type=str, help='Groq API key for description step')
    args = parser.parse_args()
    
    # Check requirements
    check_requirements()
    
    # Set up steps
    steps = {
        'scrape': {
            'name': 'Lyrics Scraping',
            'script': 'lyrics-scraper.py'
        },
        'preprocess': {
            'name': 'Data Preprocessing',
            'script': 'preprocess.py'
        },
        'romanize': {
            'name': 'Lyrics Romanization',
            'script': 'romanize.py'
        },
        'split': {
            'name': 'Verse Splitting',
            'script': 'split_verses.py' 
        },
        'describe': {
            'name': 'Verse Description Generation',
            'script': 'lyrics_describe.py',
            'args': ['--api-key', args.groq_key] if args.groq_key else []
        }
    }
    
    # Determine which steps to run
    steps_to_run = list(steps.keys()) if 'all' in args.steps else args.steps
    
    # Create necessary directories
    Path('lyrics').mkdir(exist_ok=True)
    Path('batches').mkdir(exist_ok=True)
    
    # Run the selected steps
    for step_id in steps_to_run:
        step = steps[step_id]
        step_args = step.get('args', [])
        success = run_step(step['name'], step['script'], step_args)
        if not success and step_id != steps_to_run[-1]:
            response = input(f"\n{step['name']} failed. Continue with next step? (y/n): ")
            if response.lower() != 'y':
                print("Pipeline execution stopped.")
                break

    print("\nPipeline execution completed.")

if __name__ == "__main__":
    main()
