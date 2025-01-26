import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Define the base URL and years to scrape
base_url = "https://www.federalreserve.gov/monetarypolicy/fomchistorical"
years = range(1940, 2013)

# Helper function to generate URLs
def generate_url(year):
    return f"{base_url}{year}.htm"

# Scrape FOMC dates for years before 2013
def scrape_fomc_dates(urls):
    dates = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        headings = soup.select('div.panel-heading')
        for heading in headings:
            date_text = heading.get_text(strip=True)
            if "Meeting" in date_text:
                parts = re.split(r"Meeting - ", date_text)
                if len(parts) == 2:
                    dates.append(parts[0].strip() + " " + parts[1].strip())
    return pd.DataFrame(dates, columns=["Date"])

# Generate URLs and scrape data
urls = [generate_url(year) for year in years]
dates_pre_2013 = scrape_fomc_dates(urls)

# Scrape FOMC dates for 2013 and later
def scrape_post_2013(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    panels = soup.select("div.panel.panel-default")
    records = []
    for panel in panels:
        year = panel.select_one("div.panel-heading").get_text(strip=True).split(" FOMC")[0]
        months = [m.get_text(strip=True) for m in panel.select("div.fomc-meeting__month")]
        days = [d.get_text(strip=True) for d in panel.select("div.fomc-meeting__date")]
        for month, day in zip(months, days):
            if "-" in day:
                start_day, end_day = day.split("-")
            else:
                start_day = end_day = day
            records.append([f"{start_day}/{month}/{year}", f"{end_day}/{month}/{year}", 1])
    return pd.DataFrame(records, columns=["Start", "End", "Scheduled"])

# Scrape data for 2013 and later
post_2013_url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
dates_post_2013 = scrape_post_2013(post_2013_url)

# Combine data and save to CSV
calendar_data = pd.concat([dates_pre_2013, dates_post_2013], ignore_index=True)
calendar_data.to_csv("FOMC_dates.csv", index=False)