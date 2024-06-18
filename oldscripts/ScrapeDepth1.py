import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from requests.exceptions import RequestException, Timeout
import logging
import csv
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
REQUEST_TIMEOUT = 10  # seconds
OUTPUT_FILE = 'external_links.csv'  # Output file name
SUBPAGES_OUTPUT_FILE = 'external_links_subpages.csv'  # Output file name for subpages
CONTACT_INFO_FILE = 'contact_info.csv'  # Output file name for contact information

# Function to check if a URL is an external link
def is_external_link(url, base_domain_keyword):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    # Check if the domain or the entire URL contains the base domain keyword
    if base_domain_keyword in domain or base_domain_keyword in url:
        return False
    return True

# Function to clean up company names by removing extra spaces
def clean_company_name(name):
    return re.sub(r'\s+', ' ', name).strip()

# Function to get external links and their associated company names from a given URL
def get_external_links_and_names(url):
    logging.info(f"Fetching external links from {url}")
    base_domain = urlparse(url).netloc
    base_domain_keyword = base_domain.split('.')[-2]  # Extract the main keyword from the domain
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        
        external_links = []
        for link in links:
            href = link['href']
            full_url = urljoin(url, href)
            # Extract the company name from the text following "Visit the" or "Visit"
            text = link.get_text(strip=True)
            if "Visit the" in text:
                company_name = text.split("Visit the", 1)[-1].strip()
            elif "Visit" in text:
                company_name = text.split("Visit", 1)[-1].strip()
            else:
                company_name = None
            
            if company_name:
                company_name = clean_company_name(company_name)

            if href.startswith('http') and is_external_link(full_url, base_domain_keyword):
                external_links.append((full_url, company_name))
        
        logging.info(f"Found {len(external_links)} external links")
        return external_links
    except (RequestException, Timeout) as e:
        logging.error(f"Failed to fetch external links from {url}: {e}")
        return []

# Function to get all subpages from a given URL
def get_subpages(url):
    logging.info(f"Fetching subpages from {url}")
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        
        subpages = set()
        for link in links:
            href = link['href']
            full_url = urljoin(url, href)
            if full_url.startswith(url) and not any(full_url.lower().endswith(ext) for ext in ['jpg', 'jpeg', 'png', 'gif', 'pdf']):
                subpages.add(full_url)
        
        logging.info(f"Found {len(subpages)} subpages for {url}")
        return list(subpages)
    except (RequestException, Timeout) as e:
        logging.error(f"Failed to fetch subpages from {url}: {e}")
        return []

# Function to find contact page or fallback to homepage
def find_contact_page(subpages, homepage):
    for subpage in subpages:
        if 'contact' in subpage.lower() or 'contacts' in subpage.lower():
            return subpage
    return homepage

# Function to extract contact information from a URL
def extract_contact_info(url):
    logging.info(f"Extracting contact information from {url}")
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        phones = re.findall(r'\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{1,4}\)?[-.\s]?)?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b', text)
        
        return emails, phones
    except (RequestException, Timeout) as e:
        logging.error(f"Failed to extract contact information from {url}: {e}")
        return [], []

# Function to write external links and company names to a CSV file
def write_to_csv(data, filename):
    logging.info(f"Writing external links and company names to {filename}")
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL', 'Company Name'])
        for url, company_name in data:
            writer.writerow([url, company_name])
    logging.info(f"External links and company names written to {filename}")

# Function to write subpages to a CSV file
def write_subpages_to_csv(data, filename):
    logging.info(f"Writing subpages to {filename}")
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL', 'Subpage'])
        for url, subpages in data.items():
            for subpage in subpages:
                writer.writerow([url, subpage])
    logging.info(f"Subpages written to {filename}")

# Function to write contact information to a CSV file
def write_contact_info_to_csv(data, filename):
    logging.info(f"Writing contact information to {filename}")
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL', 'Emails', 'Phones'])
        for url, contact_info in data.items():
            emails, phones = contact_info
            writer.writerow([url, ', '.join(emails), ', '.join(phones)])
    logging.info(f"Contact information written to {filename}")

# Example usage
if __name__ == "__main__":
    url = "https://www.monnit.com/partner/current-partners/"  # Replace with the target URL
    external_links_and_names = get_external_links_and_names(url)
    write_to_csv(external_links_and_names, OUTPUT_FILE)
    
    external_links_subpages = {}
    contact_info = {}
    for link, _ in external_links_and_names:
        subpages = get_subpages(link)
        external_links_subpages[link] = subpages
        contact_page = find_contact_page(subpages, link)
        emails, phones = extract_contact_info(contact_page)
        contact_info[link] = (emails, phones)
    
    write_subpages_to_csv(external_links_subpages, SUBPAGES_OUTPUT_FILE)
    write_contact_info_to_csv(contact_info, CONTACT_INFO_FILE)
    
    for link, company_name in external_links_and_names:
        print(f"URL: {link}, Company Name: {company_name}")
    
    for link, subpages in external_links_subpages.items():
        print(f"URL: {link}, Subpages: {subpages}")
    
    for link, info in contact_info.items():
        emails, phones = info
        print(f"URL: {link}, Emails: {emails}, Phones: {phones}")
