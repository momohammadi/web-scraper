import asyncio
import aiohttp
import re
import csv
from bs4 import BeautifulSoup

SEARCH_STRING = 'israel'

# Function to check if the given URL contains the searched string (case-insensitive)
async def check_url(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                for tag in soup.find_all(string=re.compile(re.escape(SEARCH_STRING), re.IGNORECASE)):
                    element = tag.find_parent()
                    line_number = html_content.count('\n', 0, html_content.find(str(tag))) + 1
                    return url, line_number, tag.parent.name, element.prettify()
    except Exception as e:
        print(f"Error accessing URL {url}: {e}")
    return None

# Read URLs from the input file
def read_urls_from_file(filename):
    with open(filename, 'r') as file:
        return file.readlines()

# Write matching URLs to the report file in CSV format
def write_report(report_filename, matching_urls):
    with open(report_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['link', 'line', 'element', 'HTML']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for url, line, element, html in matching_urls:
            writer.writerow({'link': url.strip(), 'line': line, 'element': element, 'HTML': html.strip()})

async def main():
    input_filename = 'input.txt'  # File containing URLs, one per line
    report_filename = 'report.csv'  # File to write matching URLs in CSV format

    urls = read_urls_from_file(input_filename)
    matching_urls = []

    async with aiohttp.ClientSession() as session:
        tasks = [check_url(session, url.strip()) for url in urls]
        results = await asyncio.gather(*tasks)

    for result in results:
        if result:
            matching_urls.append(result)

    write_report(report_filename, matching_urls)
    print("Report generated successfully.")

if __name__ == "__main__":
    asyncio.run(main())
