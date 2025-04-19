import requests
import logging
import time
import random
from bs4 import BeautifulSoup
import re

class JobScraper:
    def __init__(self):
        self.gendered_keywords = {
            'masculine': ['he', 'him', 'his', 'man', 'men', 'guy', 'guys'],
            'feminine': ['she', 'her', 'hers', 'woman', 'women', 'girl', 'girls']
        }
        
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
        
    def build_github_jobs_url(self, job_title, location):
        """Build GitHub Jobs API URL with job title and location"""
        base_url = "https://jobs.github.com/positions.json"
        params = {
            'description': job_title,
            'location': location,
            'full_time': 'true'
        }
        return base_url, params
            
    def scrape_jobs(self, job_title, location):
        """Scrape job listings from GitHub Jobs API"""
        try:
            # Build the GitHub Jobs API URL
            base_url, params = self.build_github_jobs_url(job_title, location)
            logging.info(f"Searching GitHub Jobs for: {job_title} in {location}")
            
            # Make API request
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            jobs_data = response.json()
            jobs = []
            
            for job_data in jobs_data:
                try:
                    # Clean HTML from description
                    description = self.clean_html(job_data.get('description', ''))
                    
                    job = {
                        'title': job_data.get('title', ''),
                        'company': job_data.get('company', ''),
                        'location': job_data.get('location', 'Not specified'),
                        'description': description,
                        'url': job_data.get('url', ''),
                        'source': 'GitHub Jobs'
                    }
                    
                    # Check for gender-neutral language
                    if not self.check_gender_neutrality(job['description']):
                        logging.warning(f"Job description contains gendered language: {job['title']}")
                        continue
                        
                    jobs.append(job)
                    
                except Exception as e:
                    logging.error(f"Error processing job data: {str(e)}")
                    continue
                    
            return jobs
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error making API request: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Error scraping jobs: {str(e)}")
            return []
            
    def close(self):
        """No cleanup needed for API-based scraper"""
        pass 