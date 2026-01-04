#!/usr/bin/env python3
"""
Fetch and update Wordle used words list
Runs daily via GitHub Actions at 2am London time
"""

import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re

def fetch_from_rock_paper_shotgun():
    """
    Fetch used words from Rock Paper Shotgun
    Most reliable source, constantly updated
    """
    url = "https://www.rockpapershotgun.com/wordle-past-answers"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all text content
        text = soup.get_text()

        # Extract 5-letter words in uppercase
        # Wordle answers are always 5 letters, uppercase
        words = re.findall(r'\b[A-Z]{5}\b', text)

        # Also fetch latest words from daily hint pages (RPS archive can be slow to update)
        daily_words = fetch_latest_daily_words(soup)
        words.extend(daily_words)

        # Remove duplicates and sort
        unique_words = sorted(set(words))

        print(f"✅ Found {len(unique_words)} words from Rock Paper Shotgun")
        return unique_words

    except Exception as e:
        print(f"❌ Error fetching from Rock Paper Shotgun: {e}")
        return None


def fetch_latest_daily_words(soup):
    """
    Fetch words from the latest daily hint pages
    RPS archive list can be slow to update, so we scrape recent daily pages
    """
    words = []

    try:
        # Find links to daily Wordle hint pages
        links = soup.find_all('a', href=True)
        daily_urls = []

        for link in links:
            href = link['href']
            # Match daily hint page URLs like /wordle-hint-and-answer-today-04-01-26
            if 'wordle-hint-and-answer' in href and href not in daily_urls:
                if not href.startswith('http'):
                    href = f"https://www.rockpapershotgun.com{href}"
                daily_urls.append(href)

        # Fetch up to 5 most recent daily pages
        for url in daily_urls[:5]:
            try:
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    daily_soup = BeautifulSoup(resp.text, 'html.parser')

                    # Look for the answer - usually in bold or strong tags near "answer"
                    text = daily_soup.get_text()

                    # Find 5-letter uppercase words
                    found = re.findall(r'\b[A-Z]{5}\b', text)
                    words.extend(found)

            except Exception:
                continue

        if words:
            print(f"📰 Found {len(set(words))} words from daily pages")

    except Exception as e:
        print(f"⚠️ Could not fetch daily pages: {e}")

    return words

def fetch_from_nyt_wordle():
    """
    Fetch from NYT Wordle game code
    Backup source
    """
    url = "https://www.nytimes.com/games/wordle/index.html"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Look for the JavaScript file containing word list
        js_urls = re.findall(r'src="([^"]*\.js)"', response.text)

        for js_url in js_urls:
            if not js_url.startswith('http'):
                js_url = f"https://www.nytimes.com{js_url}"

            js_response = requests.get(js_url, timeout=30)

            # Look for word list patterns in JS
            # NYT stores past answers in their code
            matches = re.findall(r'\b[A-Z]{5}\b', js_response.text)

            if len(matches) > 100:  # Valid word list should have many words
                unique_words = sorted(set(matches))
                print(f"✅ Found {len(unique_words)} words from NYT")
                return unique_words

        return None

    except Exception as e:
        print(f"❌ Error fetching from NYT: {e}")
        return None

def fetch_from_wordle_archive():
    """
    Fetch from Wordle Archive
    Another backup source
    """
    url = "https://www.wordlearchive.com/"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        words = re.findall(r'\b[A-Z]{5}\b', text)
        unique_words = sorted(set(words))

        print(f"✅ Found {len(unique_words)} words from Wordle Archive")
        return unique_words

    except Exception as e:
        print(f"❌ Error fetching from Wordle Archive: {e}")
        return None

def load_existing_words():
    """Load existing words from JSON file"""
    try:
        with open('used-words.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("ℹ️ No existing file found, starting fresh")
        return []

def save_words(words):
    """Save words to JSON file"""
    with open('used-words.json', 'w') as f:
        json.dump(words, f, indent=2)

    print(f"✅ Saved {len(words)} words to used-words.json")

def validate_words(words):
    """Ensure all words are valid 5-letter uppercase words"""
    valid_words = []

    for word in words:
        # Must be exactly 5 letters
        if len(word) != 5:
            continue

        # Must be all letters
        if not word.isalpha():
            continue

        # Convert to uppercase
        word = word.upper()

        valid_words.append(word)

    # Remove duplicates and sort
    return sorted(set(valid_words))

def main():
    print("🔄 Starting Wordle used words update...")
    print(f"📅 Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load existing words
    existing_words = load_existing_words()
    print(f"📊 Existing words: {len(existing_words)}")

    # Try sources in order of reliability
    new_words = None

    # Try Rock Paper Shotgun first (most reliable)
    new_words = fetch_from_rock_paper_shotgun()

    # Try NYT as backup
    if not new_words or len(new_words) < 100:
        print("⚠️ Trying NYT as backup...")
        new_words = fetch_from_nyt_wordle()

    # Try Wordle Archive as last resort
    if not new_words or len(new_words) < 100:
        print("⚠️ Trying Wordle Archive as backup...")
        new_words = fetch_from_wordle_archive()

    # If all sources failed, keep existing
    if not new_words:
        print("❌ All sources failed, keeping existing words")
        new_words = existing_words

    # Validate and clean
    clean_words = validate_words(new_words)

    # Compare with existing
    if set(clean_words) == set(existing_words):
        print("ℹ️ No new words found, file unchanged")
    else:
        added = len(clean_words) - len(existing_words)
        print(f"✅ Update complete! Added {added} new words")

    # Save
    save_words(clean_words)

    print("✅ Done!")

if __name__ == "__main__":
    main()
