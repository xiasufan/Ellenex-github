import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import csv

# Global counter for processed URLs
processed_count = 0

def extract_email(url, driver):
    global processed_count
    try:
        driver.get(url)
        # Wait for the page to load, maximum wait time of 2 seconds
        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-email]'))
            )
        except TimeoutException:
            print(f"Timeout waiting for page to load: {url}")
            processed_count += 1
            print(f"Processed URLs: {processed_count}")
            return None

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the element with the data-email attribute
        email_element = soup.find('a', attrs={'data-email': True})
        if email_element and 'data-email' in email_element.attrs:
            email = email_element['data-email']
            print(f"Extracted email from data-email attribute: {email} from {url}")
            processed_count += 1
            print(f"Processed URLs: {processed_count}")
            return email
        
        print(f"No email found on {url}")
    except WebDriverException as e:
        print(f"Error fetching {url}: {e}")
    processed_count += 1
    print(f"Processed URLs: {processed_count}")
    return None

def process_urls(urls, driver_path, writer):
    options = Options()
    options.headless = True  # Headless mode
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    for url in urls:
        email = extract_email(url, driver)
        writer.writerow({'Detail_page': url, 'email': email})

    driver.quit()

def process_csv_files():
    global processed_count
    driver_path = 'C:/Users/Max/Desktop/intern/chromedriver-win64/chromedriver.exe'  # Replace with your chromedriver path

    # Get all CSV files in the current directory
    csv_files = [file for file in os.listdir() if file.endswith('.csv')]
    print(f"Found {len(csv_files)} CSV files: {csv_files}")

    for csv_file in csv_files:
        print(f"Processing file: {csv_file}")
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            print(f"Read {len(df)} rows from {csv_file}")
            
            # Check if 'Detail_page' column exists
            if 'Detail_page' not in df.columns:
                print(f"'Detail_page' column not found in {csv_file}")
                continue

            urls = df['Detail_page'].tolist()
            batch_size = 50  # Process 50 URLs at a time
            processed_count = 0  # Reset counter for each file

            # Open a new CSV file to write processed data
            processed_csv_file = os.path.splitext(csv_file)[0] + '_processed.csv'
            with open(processed_csv_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['Detail_page', 'email']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = []
                    for i in range(0, len(urls), batch_size):
                        batch_urls = urls[i:i + batch_size]
                        futures.append(executor.submit(process_urls, batch_urls, driver_path, writer))

                    for future in as_completed(futures):
                        future.result()

            print(f"Updated file saved: {processed_csv_file}")
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")

if __name__ == "__main__":
    process_csv_files()
