import sys
from src.cricket_scraper import CricketScraper
from src.config import Config

def main():
    config = Config()
    scraper = CricketScraper(config)
    
    try:
        scraper.run()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()