# Scrapelyzer - Web Scraping Module

This module handles web scraping for job listings, events, and mentorship opportunities.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your environment variables in `.env`:
- `STORAGE_TYPE`: Choose between 'json' or 'mongodb'
- `MONGO_URI`: MongoDB connection string (required if using MongoDB)
- `USER_AGENT`: Custom user agent for web requests
- `RATE_LIMIT`: Delay between requests in seconds

## Project Structure

```
scrapers/
├── base_scraper.py     # Base scraper class with common functionality
├── job_scraper.py      # Job listings scraper
├── data_storage.py     # Data storage handler
├── main.py            # Main script to run scrapers
└── .env               # Configuration file
```

## Usage

1. Update the job board URLs in `main.py` with your target websites.

2. Run the scraper:
```bash
python -m scrapers.main
```

The scraper will:
- Check robots.txt for each website
- Respect rate limits
- Detect and log gender-biased language
- Save results to JSON or MongoDB

## Features

- **Ethical Scraping**: Respects robots.txt and implements rate limiting
- **Gender Bias Detection**: Identifies potentially gendered language in job descriptions
- **Flexible Storage**: Supports both JSON and MongoDB storage
- **Error Handling**: Comprehensive logging and error handling
- **Rate Limiting**: Configurable delay between requests

## Contributing

When adding new scrapers:
1. Inherit from `BaseScraper`
2. Implement the `extract_data` method
3. Add appropriate error handling and logging
4. Test with the target website's robots.txt
