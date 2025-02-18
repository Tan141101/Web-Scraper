import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tabula
import pandas as pd
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def restart_session(session, base_url):
    """
    Tries to restart the session by calling the /eprocure/app?service=restart URL.
    This is a workaround if we detect our session has expired.
    """
    restart_url = urljoin(base_url, "/eprocure/app?service=restart")
    restart_response = session.get(restart_url)
    restart_response.raise_for_status()
    return restart_response

def download_pdf_using_selenium(url, download_dir):
    """
    Use Selenium to click the "Print" link and download the PDF.
    """
    # Set up Chrome options to handle the automatic download of PDF files
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode (no UI)
    chrome_options.add_argument('--disable-gpu')  # Disable GPU (for headless mode)
    chrome_options.add_argument(f'--download-default-directory={download_dir}')  # Set the download directory

    # Initialize WebDriver (Chrome in this case)
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Open the URL
        driver.get(url)
        
        # Wait for the page to load completely (you may need to adjust the time)
        time.sleep(25)

        # Find the 'Print' link and click it (use XPath or CSS selectors)
        print_link = driver.find_element(By.XPATH, '//a[@title="Print"]')  # Find by title="Print"
        print_link.click()

        # Wait for the print dialog to trigger and the download to start (adjust timing as needed)
        time.sleep(5)  # You may need to adjust this depending on page load and download speed

        # Check the download folder for the PDF file (the name might be auto-generated)
        print(f"PDF should be downloaded in {download_dir}")
        
    finally:
        driver.quit()

def scrape_view_more_details(url, download_dir):
    """
    1. Attempt to fetch the main page.
    2. If session is stale or timed out, restart it.
    3. Locate 'View More Details' link and open the popup page.
    4. On that popup page, find the 'Print' link and download the PDF.
    5. Extract tables from the PDF using tabula and return JSON data.
    """
    session = requests.Session()

    # Step 1: Fetch the initial page
    response = session.get(url)
    
    # Check if the session is timed out (or user is returned to login)
    if "Your session has timed out" in response.text:
        # If session is stale, try restarting it
        restart_session(session, url)
        # Now reattempt to fetch the main page after restarting session
        response = session.get(url)
    
    # Make sure we have a valid response at this point
    response.raise_for_status()

    # Parse the main page HTML
    soup_main = BeautifulSoup(response.text, 'html.parser')

    # Step 2: Find the "View More Details" link
    view_details_link = soup_main.find('a', {'title': 'View More Details'})
    if not view_details_link:
        raise ValueError("Could not find the 'View More Details' link on the page. Adjust selectors.")

    # Build the popup URL (relative -> absolute)
    popup_partial_url = view_details_link.get('href')
    print(popup_partial_url)
    if not popup_partial_url:
        raise ValueError("No href found on 'View More Details' link.")
    popup_url = urljoin(url, popup_partial_url)

    # Step 3: Fetch the popup page
    popup_response = session.get(popup_url)
    popup_response.raise_for_status()

    soup_popup = BeautifulSoup(popup_response.text, 'html.parser')
    print(popup_url)

    # Step 4: Locate the "Print" / PDF link (use Selenium to trigger this action)
    # Step 5: Download the PDF using Selenium
    download_pdf_using_selenium(popup_url, download_dir)

    # Step 6: Extract tables from the downloaded PDF using tabula
    pdf_filename = os.path.join(download_dir, 'downloaded_popup.pdf')

    # Ensure the file exists before trying to process
    if not os.path.exists(pdf_filename):
        raise ValueError(f"PDF file not found in {download_dir}. Download might have failed.")

    # Extract tables from PDF using tabula
    try:
        dataframes = tabula.read_pdf(pdf_filename, pages='all')
    except Exception as e:
        raise RuntimeError(f"Error reading tables from PDF using tabula: {e}")

    # Convert each DataFrame into JSON
    tables_json = []
    for idx, df in enumerate(dataframes):
        tables_json.append({
            "table_index": idx,
            "data": df.to_dict(orient='records')
        })

    return tables_json


if __name__ == "__main__":
    # Example usage: Replace with a real URL that includes the "View More Details" link
    main_url = "https://eprocure.gov.in/eprocure/app?component=%24DirectLink&page=FrontEndViewTender&service=direct&session=T&sp=SaX4gJXw%2FXlBuJozDojuwzw%3D%3D"
    download_dir = os.path.join(os.getcwd(), "downloads")  # Set the desired download directory

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    try:
        extracted_pdf_tables = scrape_view_more_details(main_url, download_dir)
        # Print out as JSON
        print(json.dumps(extracted_pdf_tables, indent=2))
    except Exception as e:
        print(f"An error occurred: {e}")
