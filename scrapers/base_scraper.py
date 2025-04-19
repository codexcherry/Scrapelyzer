import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
import logging
from urllib.robotparser import RobotFileParser

class BaseScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(f"{base_url}/robots.txt")
        self.robot_parser.read()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    def can_fetch(self, url: str) -> bool:
        """Check if we're allowed to scrape the given URL according to robots.txt"""
        return self.robot_parser.can_fetch(self.session.headers['User-Agent'], url)

    def get_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a webpage with rate limiting and error handling"""
        if not self.can_fetch(url):
            self.logger.warning(f"Scraping not allowed for URL: {url}")
            return None

        try:
            response = self.session.get(url)
            response.raise_for_status()
            time.sleep(1)  # Basic rate limiting
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def clean_text(self, text: str) -> str:
        """Clean and normalize text data"""
        if not text:
            return ""
        return " ".join(text.strip().split())

    def extract_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """To be implemented by child classes"""
        raise NotImplementedError("Child classes must implement extract_data method")

    def scrape(self, url: str) -> List[Dict[str, Any]]:
        """Main scraping method that handles the entire process"""
        soup = self.get_page(url)
        if not soup:
            return []
        
        try:
            data = self.extract_data(soup)
            self.logger.info(f"Successfully scraped {len(data)} items from {url}")
            return data
        except Exception as e:
            self.logger.error(f"Error extracting data from {url}: {str(e)}")
            return [] 