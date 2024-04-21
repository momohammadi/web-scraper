import asyncio
import aiohttp
import re
import csv
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

SEARCH_STRING = 'ded9.com'

# Function to check if the given URL contains the searched string (case-insensitive)
async def check_url(session, url, success_progress_bar, non_matching_urls):
    try:
        start_time = time.time()
        async with session.get(url) as response:
            elapsed_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            if response.status == 200:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                for tag in soup.find_all(string=re.compile(re.escape(SEARCH_STRING), re.IGNORECASE)):
                    element = tag.find_parent()
                    line_number = html_content.count('\n', 0, html_content.find(str(tag))) + 1
                    success_progress_bar.update(1)
                    return url, line_number, tag.parent.name, element.prettify(), elapsed_time
                non_matching_urls.append(url)
            else:
                return url, f"{response.status} {response.reason}", elapsed_time
    except Exception as e:
        print(f"Error accessing URL {url}: {e}")
        return url, f"Error: {e}", 0

# Read URLs from the input file
def read_urls_from_file(filename):
    with open(filename, 'r') as file:
        return file.readlines()

# Write matching URLs to the success report file in CSV format
def write_success_report(success_report_filename, matching_urls):
    with open(success_report_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['link', 'line', 'element', 'HTML', 'time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for url, line, element, html, elapsed_time in matching_urls:
            writer.writerow({'link': url.strip(), 'line': line, 'element': element, 'HTML': html.strip(), 'time': elapsed_time})

# Write error URLs to the error report file in CSV format
def write_error_report(error_report_filename, error_urls):
    with open(error_report_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['link', 'error', 'time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for url, error, elapsed_time in error_urls:
            writer.writerow({'link': url.strip(), 'error': error, 'time': elapsed_time})

# Write non-matching URLs to the non-matching report file in CSV format
def write_non_matching_report(non_matching_report_filename, non_matching_urls):
    with open(non_matching_report_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for url in non_matching_urls:
            writer.writerow({'link': url.strip()})

async def main():
    input_filename = 'input.txt'  # File containing URLs, one per line
    success_report_filename = 'success_report.csv'  # File to write success report in CSV format
    error_report_filename = 'error_report.csv'  # File to write error report in CSV format
    non_matching_report_filename = 'non_matching_report.csv'  # File to write non-matching report in CSV format

    urls = read_urls_from_file(input_filename)
    matching_urls = []
    error_urls = []
    non_matching_urls = []

    async with aiohttp.ClientSession() as session:
        total_urls = len(urls)
        success_progress_bar = tqdm(total=total_urls, desc="Overall Progress", position=0)

        for url in urls:
            url = url.strip()
            result = await check_url(session, url, success_progress_bar, non_matching_urls)
            if result:
                if len(result) == 5:
                    matching_urls.append(result[:-1])  # Exclude elapsed_time for success report
                else:
                    error_urls.append(result)
            success_progress_bar.update(1)

        success_progress_bar.close()

    write_success_report(success_report_filename, matching_urls)
    write_error_report(error_report_filename, error_urls)
    write_non_matching_report(non_matching_report_filename, non_matching_urls)
    print("Reports generated successfully.")

if __name__ == "__main__":
    asyncio.run(main())
