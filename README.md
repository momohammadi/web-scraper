# Web Scraper Script

This script allows you to scrape web pages for content matching a specific search string or find domain differences between two files.

## General Information

You can use this script directly or via Docker and also by command line arguments or environment variables.

##### Available environment variables:

- `OPTION`: Specify the operation to perform ('scrap' for web scraping or 'def' for domain difference finding).
- `SOURCE_FILE`: Path to the source file (for web scraping).
- `FIRST_FILE`: Path to the first file (for domain difference finding).
- `SECOND_FILE`: Path to the second file (for domain difference finding).
- `SEARCH_STRING`: The string to search for in web pages (for scraping).
- `TIMEOUT`: The timeout in seconds for checking every web link.

##### Available option:

   - **scrap**: Scrap web links to search for your string and generate report files of matching or non-matching URLs. URLs are read from a TXT file separated by lines.
  
   - **def**: Finding the domain list from the first file not in the second file and generating a report file under the "reports" directory named "domain_difference.txt". The Input Files for "def" could be TXT or CSV. If you use CSV format, you should have a "link" header, and all links or domains should be under this column. Using a TXT file, you should separate each link or domain per line.

##### Prepare Input File:
  - **scrap**: Place the source file containing the URLs or the Links to be scraped and set the path to the `SOURCE_FILE` environment variable. Each URL or LINK should be on a separate line.
  - **def**: Place two files named "first" and "second", or any names you prefer. Then, for a TXT file, separate the URLs or the Links on each line. For a CSV file, add a "link" header and insert your URLs or links into this column.

## Direct Usage
1. Clone the repository:
```bash
git clone https://github.com/momohammadi/web-scraper.git
```
2. Navigate to the project directory:
```bash
cd web-scraper/
```
3. Install Dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Script:
```bash
python app.py --option <scrap/def> --source_file <path_to_source_file> --first_file <path_to_first_file> --second_file <path_to_second_file> --timeout 10 --search_string searchString
```

## Docker Usage
1. Clone the repository:
```bash
git clone https://github.com/momohammadi/web-scraper.git
```
2. Navigate to the project directory:
```bash
cd web-scraper/
```
3. Create the Environment Variable File:
```bash
cp envsample .env
```
4. Edit the .env file as needed by your preferred editor and set the value of each variable

5. Build and Run the Docker Container:
```bash
docker compose up
```
This command will build the Docker image, run the script inside a Docker container, and then remove the created container.

## View Reports:
The matched report will be saved as reports/match_report.csv.

Error report will be saved as reports/error_report.csv.

Non-matching report will be saved as reports/non_matching_report.csv.
