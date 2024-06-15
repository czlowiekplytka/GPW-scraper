import re
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def clean_headline(headline):
    # Example cleaning operations
    # Remove leading and trailing whitespace
    cleaned = headline.strip()
    return cleaned

def get_news(url):
    print(f"Scraping {url}...")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.find_all('li', class_='cmp-report-list__item')
    
    headlines_and_data = []
    base_url = 'https://www.orlen.pl'  # Base URL for relative links
    
    for item in items:
        # Extract headline
        title_tag = item.find('p', class_='cmp-report-list__title')
        headline = title_tag.get_text(strip=True) if title_tag else 'No title found'
        
        # Extract link
        link_tag = item.find('a', class_='cmp-report-list__link')
        link = base_url + link_tag['href'] if link_tag and link_tag['href'].startswith('/') else link_tag['href'] if link_tag else ''
        
        # Extract report number
        report_number_tag = item.find('span', class_='cmp-report-list__reportNumber')
        report_number = report_number_tag.get_text(strip=True)[-7:] if report_number_tag else ''
        
        # Extract publication date
        publication_date_tag = item.find('span', class_='cmp-report-list__publicationDate')
        publication_date = publication_date_tag.get_text(strip=True) if publication_date_tag else ''
        
        # Clean headline
        cleaned_headline = clean_headline(headline)
        
        # Append to list
        headlines_and_data.append((report_number, publication_date, cleaned_headline, link))
    
    if not headlines_and_data:
        print("No headlines found.")
    
    return headlines_and_data

# List of news websites to scrape
news_urls = [
    'https://www.orlen.pl/pl/relacje-inwestorskie/raporty-i-publikacje/raporty-biezace',
    # Add more URLs here
]

all_headlines_and_data = []
for url in news_urls:
    all_headlines_and_data.extend(get_news(url))

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# Below give path to JSON for your Gcloud
creds = ServiceAccountCredentials.from_json_keyfile_name('INPUT JSON', scope)
# _____________________________________

client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open('Scraper').sheet1

# Check existing rows to avoid duplicates
existing_rows = sheet.get_all_values()
existing_headlines = [row[2] for row in existing_rows[1:]]  # Assuming headlines are in the third column (index 2)

# Write headlines, report numbers, publication dates, and links to Google Sheet
for report_number, publication_date, headline, link in all_headlines_and_data:
    if headline not in existing_headlines:
        sheet.append_row([report_number, publication_date, headline, link])
    else:
        print(f"Skipped duplicate headline: {headline}")

print("All data processed.")
