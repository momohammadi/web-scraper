"""
Web Scraper Script

This script allows you to scrape web pages for content matching a specific search string.

Author: Morteza Saeed Mohammadi
Email: m.mohammadi721@gmail.com
GitHub: https://github.com/momohammadi/
Date: April 2024
"""

import asyncio
import aiohttp
import re
import csv
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import argparse
from urllib.parse import urlparse

first_file = os.environ.get('FIRST_FILE')
first_file = os.environ.get('SECOND_FILE')


SEARCH_STRING = 'stringToSearch' # Set Your string to search for in the web links
TIMEOUT = 10  # Timeout value in seconds

# Function to read URLs from the input file
def read_urls_from_file(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"The input file '{filename}' does not exist.")

    urls = []
    with open(filename, 'r') as file:
        if filename.endswith('.txt'):
            # Read links from TXT file (one per line)
            urls.extend(file.readlines())
        elif filename.endswith('.csv'):
            # Read links from CSV file (from specified header)
            reader = csv.DictReader(file)
            for row in reader:
                if 'link' in row:
                    urls.append(row['link'])
                else:
                    raise ValueError("CSV file must contain a 'link' header.")
        else:
            raise ValueError("Unsupported file format. Only TXT and CSV files are supported.")

    return urls

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

# Function to ensure the 'reports' directory exists
def ensure_reports_directory_exists():
    if not os.path.isdir('reports'):
        raise FileNotFoundError("The 'reports' directory does not exist.")

# Write matching URLs to the success report file in CSV format
def write_success_report(success_report_filename, matching_urls):
    try:
        ensure_reports_directory_exists()
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
        ensure_reports_directory_exists()
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
        ensure_reports_directory_exists()
        with open(non_matching_report_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for url in non_matching_urls:
                writer.writerow({'link': url.strip()})
    except Exception as e:
        print(f"Error writing non-matching report: {e}")

def extract_domain(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc:
        return parsed_url.netloc
    else:
        return url.strip()

# Function to find the difference in domain lists between two files
def find_domain_difference(first_file, second_file):
  first_domains = set(extract_domain(url) for url in read_urls_from_file(first_file))
  second_domains = set(extract_domain(url) for url in read_urls_from_file(second_file))
  difference = first_domains - second_domains
  return difference

def write_difference_to_file(difference, output_file):
    try:
        with open(output_file, 'w') as file:
            file.write("Domains in first file but not in second file are:\n")
            for domain in difference:
                file.write(domain + '\n')
        print("Difference written to", output_file)
    except Exception as e:
        print(f"Error writing difference to file: {e}")

async def main():
    parser = argparse.ArgumentParser(description='Web Scraper and Domain Difference Finder')
    parser.add_argument('option', choices=['srap', 'def'], nargs='?', help='Specify whether to perform web scraping (srap) or domain difference finding (def)')
    parser.add_argument('--first_file', nargs='?', help='Path to the second file for def option')
    parser.add_argument('--second_file', nargs='?', help='Path to the second file for def option')
    # Set default values based on environment variables
    parser.set_defaults(
        option=os.environ.get('OPTION', 'srap'),
        first_file=os.environ.get('FIRST_FILE', ''),
        second_file=os.environ.get('SECOND_FILE', '')
    )
    args = parser.parse_args()
    if args.option == 'srap':
      input_filename = 'sources/list_links.txt'  # File containing URLs, one per line
      success_report_filename = 'reports/success_report.csv'  # File to write success report in CSV format
      error_report_filename = 'reports/error_report.csv'  # File to write error report in CSV format
      non_matching_report_filename = 'reports/non_matching_report.csv'  # File to write non-matching report in CSV format

      try:
          ensure_reports_directory_exists()
          urls = read_urls_from_file(input_filename)
      except FileNotFoundError as e:
          print(e)
          return

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
    elif args.option == 'def':
      if not args.first_file:
        print("Please provide the second file path using --first_file argument")
        return
      if not args.second_file:
          print("Please provide the second file path using --second_file argument")
          return
      # Find the difference in domain lists
      difference = find_domain_difference(args.first_file, args.second_file)
      if difference:
          output_file = 'reports/domain_difference.txt'
          write_difference_to_file(difference, output_file)
      else:
          print("No difference found between domain lists.")
    else:
        print("Invalid option. Use 'srap' or 'def'.")

if __name__ == "__main__":
    asyncio.run(main())