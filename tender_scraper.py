# import requests
# from bs4 import BeautifulSoup
# import json

# # Initialize a session to maintain cookies
# session = requests.Session()

# # Set headers to mimic a real browser
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
# }

# # Step 1: Visit the homepage to initiate a session 
# base_url = "https://eprocure.gov.in/eprocure/app"
# session.get(base_url, headers=headers)

# # Step 2: Define the tender URL
# tender_url = "https://eprocure.gov.in/eprocure/app?component=$DirectLink&page=FrontEndViewTender&service=direct&session=T&sp=SE0%2BacEvtpU8ISCWvfHd7yg%3D%3D"

# # Step 3: Request the tender page
# response = session.get(tender_url, headers=headers)
# soup = BeautifulSoup(response.content, "html.parser")

# # Step 4: Extract tender metadata from tables
# tender_info = {}

# # Find all tables with class 'listtable'
# tables = soup.find_all("table", class_="list_table")
# for table in tables:
#     rows = table.find_all("tr")
#     print(rows)
#     for row in rows:
#         cells = row.find_all("td")
#         if len(cells) >= 2:
#             key = cells[0].get_text(strip=True).replace(":", "")
#             value = cells[1].get_text(strip=True)
#             tender_info[key] = value

# # Add additional metadata if available
# title = soup.find("div", class_="workitemtitle")
# tender_info["Title"] = title.get_text(strip=True) if title else "N/A"

# # Step 5: Save the tender metadata to JSON
# with open("tender_metadata.json", "w") as json_file:
#     json.dump(tender_info, json_file, indent=4)

# print("Tender metadata saved to tender_metadata.json")
import requests
from bs4 import BeautifulSoup
import json

# Initialize a session to maintain cookies
session = requests.Session()

# Set headers to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Step 1: Visit the homepage to initiate a session 
base_url = "https://eprocure.gov.in/eprocure/app"
session.get(base_url, headers=headers)

# Step 2: Define the tender URL
tender_url = "https://eprocure.gov.in/eprocure/app?component=$DirectLink&page=FrontEndViewTender&service=direct&session=T&sp=SE0%2BacEvtpU8ISCWvfHd7yg%3D%3D"

# Step 3: Request the tender page
response = session.get(tender_url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Step 4: Extract tender metadata from tables
tender_info = {}

# Find all tables with class 'list_table'
tables = soup.find_all("table", class_="list_table")
for table in tables:
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 2:
            key = cells[0].get_text(strip=True).replace(":", "")
            value = cells[1].get_text(strip=True)
            tender_info[key] = value

# Add additional metadata if available
title = soup.find("div", class_="workitemtitle")
tender_info["Title"] = title.get_text(strip=True) if title else "N/A"

# Extract document links and types
documents = []
doc_table = soup.find("table", class_="document_table")  # Adjust class as necessary
if doc_table:
    doc_rows = doc_table.find_all("tr")
    for doc_row in doc_rows:
        doc_cells = doc_row.find_all("td")
        if len(doc_cells) >= 2:
            doc_type = doc_cells[0].get_text(strip=True)
            doc_link = doc_cells[1].find('a')['href'] if doc_cells[1].find('a') else None
            documents.append({"Document Type": doc_type, "Link": doc_link})

tender_info["Documents"] = documents

# Extract additional important data from the page
additional_data = {}
meta_tags = soup.find_all("meta")
for meta in meta_tags:
    name = meta.get("name")
    content = meta.get("content")
    if name and content:
        additional_data[name] = content

# Include any other relevant sections or divs as needed
description_div = soup.find("div", class_="description")  # Change the class as per actual HTML structure
if description_div:
    tender_info["Description"] = description_div.get_text(strip=True)

# Combine additional data into tender_info
tender_info["Meta Tags"] = additional_data

# Step 5: Save the tender metadata to JSON
with open("tender_metadata.json", "w", encoding='utf-8') as json_file:
    json.dump(tender_info, json_file, ensure_ascii=False, indent=4)

print("Tender metadata saved to tender_metadata.json")
