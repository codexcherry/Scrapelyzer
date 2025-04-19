from pymongo import MongoClient
import json
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['ashaai']
collection = db['jobs']

# Fetch all jobs
jobs = list(collection.find())

# Convert ObjectId and datetime to string for JSON serialization
def convert_for_json(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

# Print each job with nice formatting
for job in jobs:
    print("\n" + "="*80)
    print(f"Title: {job['title']}")
    print(f"Company: {job['company']}")
    print(f"Salary Range: {job.get('salary_min', 'Not specified')} - {job.get('salary_max', 'Not specified')}")
    print(f"Source: {job['source']}")
    print(f"URL: {job['url']}")
    print(f"Description: {job['description'][:200]}...")  # Show first 200 chars of description
    print("="*80) 