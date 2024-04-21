import asyncio
import aiohttp
import re
import csv
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

SEARCH_STRING = 'ded9.com'
TIMEOUT = 10  # Timeout value in seconds

# Function to read URLs from the input file
def read_urls_from_file(filename):
    with open(filename, 'r') as file:
        return file.readlines()

# Function to check if the given URL contains the searched string (case-insensitive)
async def check_url(session, url, progress_bar, non_matching_urls):
    try:
        async with session.get(url, timeout=TIMEOUT, allow_redirects=True) as response:
            if response.status == 200:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                for tag in soup.find_all(string=re.compile(re.escape(SEARCH_STRING), re.IGNORECASE)):
                    element = tag.find_parent()
                    line_number = html_content.count('\n', 0, html_content.find(str(tag))) + 1
                    return url, line_number, tag.parent.name, str(element)
                non_matching_urls.append(url)
            else:
                return url, f"{response.status} {response.reason}", ''
    except asyncio.TimeoutError:
        print(f"\rTimeout accessing URL {url}", end='')
        return url, "Timeout", ''
    except Exception as e:
        print(f"\rError accessing URL {url}: {e}", end='')
        return url, f"Error: {e}", ''

# Write matching URLs to the success report file in CSV format
def write_success_report(success_report_filename, matching_urls):
    try:
        with open(success_report_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['link', 'line', 'element', 'html']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for url_info in matching_urls:
                writer.writerow({'link': url_info[0].strip(), 'line': url_info[1], 'element': url_info[2], 'html': url_info[3]})
    except Exception as e:
        print(f"Error writing success report: {e}")

# Write error URLs to the error report file in CSV format
def write_error_report(error_report_filename, error_urls):
    try:
        with open(error_report_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['link', 'error']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for url_info in error_urls:
                writer.writerow({'link': url_info[0].strip(), 'error': url_info[1]})
    except Exception as e:
        print(f"Error writing error report: {e}")

# Write non-matching URLs to the non-matching report file in CSV format
def write_non_matching_report(non_matching_report_filename, non_matching_urls):
    try:
        with open(non_matching_report_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for url in non_matching_urls:
                writer.writerow({'link': url.strip()})
    except Exception as e:
        print(f"Error writing non-matching report: {e}")

async def main():
    input_filename = 'list_links.txt'  # File containing URLs, one per line
    success_report_filename = 'reports/success_report.csv'  # File to write success report in CSV format
    error_report_filename = 'reports/error_report.csv'  # File to write error report in CSV format
    non_matching_report_filename = 'reports/non_matching_report.csv'  # File to write non-matching report in CSV format

    urls = read_urls_from_file(input_filename)
    matching_urls = []
    error_urls = []
    non_matching_urls = []

    async with aiohttp.ClientSession() as session:
        total_urls = len(urls)
        with tqdm(total=total_urls, desc="Overall Progress", position=0) as overall_progress_bar:
            for url in urls:
                url = url.strip()
                with tqdm(desc=f"Checking {url}", position=1, leave=False) as progress_bar:
                    result = await check_url(session, url, progress_bar, non_matching_urls)
                    if result:
                        if len(result) == 4:
                            matching_urls.append(result)  # Exclude elapsed_time for success report
                        else:
                            error_urls.append(result)
                overall_progress_bar.update(1)

    write_success_report(success_report_filename, matching_urls)
    write_error_report(error_report_filename, error_urls)
    write_non_matching_report(non_matching_report_filename, non_matching_urls)
    print("Reports generated successfully.")

if __name__ == "__main__":
    asyncio.run(main())
