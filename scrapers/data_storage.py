import json
import logging
import os
from datetime import datetime
from pymongo import MongoClient

class DataStorage:
    def __init__(self, storage_type='json', mongo_uri=None):
        self.storage_type = storage_type
        self.mongo_uri = mongo_uri
        self.mongo_client = None
        self.logger = logging.getLogger(__name__)
        
        if storage_type == 'mongodb' and mongo_uri:
            try:
                self.mongo_client = MongoClient(mongo_uri)
                self.logger.info("Connected to MongoDB")
            except Exception as e:
                self.logger.error(f"Error connecting to MongoDB: {str(e)}")
                self.storage_type = 'json'  # Fallback to JSON storage
                
    def store_jobs(self, jobs):
        """Store jobs data in the configured storage"""
        if not jobs:
            return
            
        # Add timestamp to each job
        timestamp = datetime.now().isoformat()
        for job in jobs:
            job['timestamp'] = timestamp
            
        if self.storage_type == 'mongodb' and self.mongo_client:
            try:
                db = self.mongo_client.get_database()
                collection = db.jobs
                collection.insert_many(jobs)
                self.logger.info(f"Stored {len(jobs)} jobs in MongoDB")
            except Exception as e:
                self.logger.error(f"Error storing jobs in MongoDB: {str(e)}")
                self._store_json(jobs)  # Fallback to JSON storage
        else:
            self._store_json(jobs)
            
    def _store_json(self, jobs):
        """Store jobs data in a JSON file"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/jobs_{timestamp}.json'
            
            # Write jobs to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Stored {len(jobs)} jobs in {filename}")
        except Exception as e:
            self.logger.error(f"Error storing jobs in JSON: {str(e)}")
            
    def close(self):
        """Close any open connections"""
        if self.mongo_client:
            self.mongo_client.close()
            self.logger.info("Closed MongoDB connection") 