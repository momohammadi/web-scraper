# Web Scraper Script
This script allows you to scrape web pages for content matching a specific search string.

## Direct Usage
1. **Install Dependencies:**
   pip install -r requirements.txt
Prepare Input File:
Place list_links.txt file containing the URLs to be scraped in the sources directory. Each URL should be on a separate line.

### Run the Script:
python app.py
This command will execute the script, scrape the web pages, and generate reports.

### View Reports:
Success report will be saved as reports/success_report.csv
Error report will be saved as reports/error_report.csv
Non-matching report will be saved as reports/non_matching_report.csv

## Docker Usage
### Prepare Input File:
Place list_links.txt file containing the URLs to be scraped in the sources directory. Each URL should be on a separate line.
### Build and Run the Docker Container:
docker compose up
This command will build the Docker image and run the script inside a Docker container.
### View Reports:
Success report will be saved as reports/success_report.csv
Error report will be saved as reports/error_report.csv
Non-matching report will be saved as reports/non_matching_report.csv

# Dependencies
python version 3
aiohttp==3.8.1
beautifulsoup4==4.10.0
tqdm==4.62.3
