import os
from dotenv import load_dotenv
from scrapers.job_scraper import JobScraper
from scrapers.data_storage import DataStorage
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Initialize data storage
    storage_type = os.getenv('STORAGE_TYPE', 'json')
    mongo_uri = os.getenv('MONGO_URI')
    
    storage = DataStorage(storage_type=storage_type, mongo_uri=mongo_uri)
    scraper = JobScraper()
    
    try:
        # Define job titles to search for
        job_titles = [
            "software developer",
            "web developer",
            "data analyst",
            "project manager",
            "ui designer",
            "qa engineer"
        ]
        
        # Location for all searches
        location = "Bengaluru, Karnataka"
        
        # Scrape jobs for each title
        all_jobs = []
        for title in job_titles:
            logger.info(f"Starting to scrape jobs for: {title} in {location}")
            jobs = scraper.scrape_jobs(title, location)
            if jobs:
                all_jobs.extend(jobs)
                logger.info(f"Found {len(jobs)} jobs for {title}")
            else:
                logger.warning(f"No jobs found for {title} in {location}")
        
        if all_jobs:
            # Store jobs in MongoDB
            storage.store_jobs(all_jobs)
            logger.info(f"Successfully stored {len(all_jobs)} jobs")
        else:
            logger.warning("No jobs were scraped successfully")
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
    finally:
        scraper.close()
        storage.close()

if __name__ == "__main__":
    main() 