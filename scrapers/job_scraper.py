import requests
import logging
import time
import random
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class JobScraper:
    def __init__(self):
        self.gendered_keywords = {
            'masculine': ['he', 'him', 'his', 'man', 'men', 'guy', 'guys'],
            'feminine': ['she', 'her', 'hers', 'woman', 'women', 'girl', 'girls']
        }
        self.logger = logging.getLogger(__name__)
        
        # Get Adzuna API credentials
        self.app_id = os.getenv('ADZUNA_APP_ID')
        self.app_key = os.getenv('ADZUNA_APP_KEY')
        
        if not self.app_id or not self.app_key:
            self.logger.error("Adzuna API credentials not found in environment variables")
        
    def check_gender_neutrality(self, text):
        """Check if text contains gender-specific language"""
        text = text.lower()
        for gender, keywords in self.gendered_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return False
        return True
        
    def clean_html(self, html):
        """Clean HTML tags from text"""
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(strip=True)
        
    def build_url(self, job_title, location):
        """Build Adzuna API URL with job title and location"""
        # Using Adzuna's search endpoint for India
        base_url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
        params = {
            'app_id': self.app_id,
            'app_key': self.app_key,
            'what': job_title,
            'where': location,
            'content-type': 'application/json',
            'results_per_page': 50,
            'max_days_old': 30,
            'sort_by': 'date',
            'full_time': 1
        }
        return base_url, params
            
    def scrape_jobs(self, job_title, location):
        """Scrape job listings with given job title and location"""
        if not self.app_id or not self.app_key:
            self.logger.error("Cannot scrape jobs without Adzuna API credentials")
            return []
            
        try:
            # Build the search URL
            base_url, params = self.build_url(job_title, location)
            self.logger.info(f"Searching Adzuna for: {job_title} in {location}")
            
            # Add headers to mimic a browser
            headers = {
                'User-Agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'),
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            # Make API request with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.get(base_url, params=params, headers=headers, timeout=10)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        self.logger.error(f"Error making API request after {max_retries} attempts: {str(e)}")
                        return []
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
            
            data = response.json()
            jobs = []
            
            for job_data in data.get('results', []):
                try:
                    # Clean HTML from description
                    description = self.clean_html(job_data.get('description', ''))
                    
                    job = {
                        'title': job_data.get('title', ''),
                        'company': job_data.get('company', {}).get('display_name', 'Not specified'),
                        'location': job_data.get('location', {}).get('display_name', 'Not specified'),
                        'description': description,
                        'url': job_data.get('redirect_url', ''),
                        'salary_min': job_data.get('salary_min'),
                        'salary_max': job_data.get('salary_max'),
                        'source': 'Adzuna'
                    }
                    
                    # Check for gender-neutral language
                    if not self.check_gender_neutrality(job['description']):
                        self.logger.warning(f"Job description contains gendered language: {job['title']}")
                        continue
                        
                    jobs.append(job)
                    
                except Exception as e:
                    self.logger.error(f"Error processing job data: {str(e)}")
                    continue
                    
            return jobs
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making API request: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Error scraping jobs: {str(e)}")
            return []
            
    def close(self):
        """No cleanup needed for API-based scraper"""
        pass 