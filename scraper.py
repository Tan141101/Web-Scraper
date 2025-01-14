import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

# URL to scrape
url = "https://eprocure.gov.in/eprocure/app?page=FrontEndTendersByOrganisation&service=page"

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Find all rows containing organization data
rows = soup.find_all("tr", id=lambda x: x and x.startswith("informal_"))

# Create a CSV file to store the results
with open("tenders.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["S.No", "Organization Name", "Tender Count", "Link"])

    # Iterate through each row and extract the data
    for row in rows:
        cells = row.find_all("td")
        sno = cells[0].get_text(strip=True)
        org_name = cells[1].get_text(strip=True)
        tender_count = cells[2].find("a").get_text(strip=True)
        link = cells[2].find("a")["href"]

        # Write to the CSV
        writer.writerow([sno, org_name, tender_count, f"https://eprocure.gov.in{link}"])

print("Scraping completed! Data saved to tenders.csv.")