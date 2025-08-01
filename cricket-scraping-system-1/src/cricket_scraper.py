import requests
from bs4 import BeautifulSoup
import logging
from .config import Config
from .database import Database

class CricketScraper:
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.db = Database()
        logging.basicConfig(filename='logs/cricket_scraper.log', level=logging.INFO)

    def fetch_match_list(self):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"Error fetching match list: {e}")
            return None

    def parse_match_list(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        matches = []
        for match in soup.select(Config.MATCH_SELECTOR):
            match_data = {
                'title': match.select_one(Config.TITLE_SELECTOR).text,
                'date': match.select_one(Config.DATE_SELECTOR).text,
                'link': match.select_one(Config.LINK_SELECTOR)['href']
            }
            matches.append(match_data)
        return matches

    def save_matches_to_db(self, matches):
        for match in matches:
            self.db.insert_match(match)

    def run(self):
        html = self.fetch_match_list()
        if html:
            matches = self.parse_match_list(html)
            self.save_matches_to_db(matches)
            logging.info(f"Saved {len(matches)} matches to the database.")

if __name__ == "__main__":
    scraper = CricketScraper()
    scraper.run()