import requests
from bs4 import BeautifulSoup
import csv

# Initialize a session to maintain cookies
session = requests.Session()

# Step 1: Visit the homepage to initiate a session
base_url = "https://eprocure.gov.in/eprocure/app"
session.get(base_url)

# Step 2: Read the first 5 tender links from the CSV file
with open("tenders.csv", "r") as file:
    reader = csv.DictReader(file)
    rows = list(reader)[:5]

# Step 3: Create a new CSV file to save tender details
with open("tender_details.csv", "w", newline="") as tender_file:
    writer = csv.writer(tender_file)
    writer.writerow(["Organization", "Tender ID", "Title", "Closing Date", "Tender Link"])

    for row in rows:
        org_name = row["Organization Name"]
        link = row["Link"]

        # Step 4: Use the session to request the tender page
        response = session.get(link)
        soup = BeautifulSoup(response.content, "html.parser")

        # Step 5: Check if the session has expired
        if "Your session has timed out" in response.text:
            print(f"Session timed out for {org_name}. Skipping...")
            continue

        # Step 6: Extract tender rows from the table
        table = soup.find("table", class_="list_table")
        if not table:
            print(f"No tender table found for {org_name}. Skipping...")
            continue

        rows = table.find_all("tr")[1:]  # Skip the header row

        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 6:
                continue

            tender_id = cells[4].get_text(strip=True)
            title = cells[4].find("a").get_text(strip=True)
            closing_date = cells[2].get_text(strip=True)
            tender_link = f"https://eprocure.gov.in{cells[4].find('a')['href']}"

            # Write each tender's details to the CSV file
            writer.writerow([org_name, tender_id, title, closing_date, tender_link])

        print(f"Tenders for {org_name} scraped successfully!")

# Close the session
session.close()
