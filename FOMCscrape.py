import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from dateutil import parser

# Define the base URL and years to scrape
BASE_URL = "https://www.federalreserve.gov/monetarypolicy/fomchistorical"
POST_2013_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
YEARS = range(1940, 2020)

# Helper function to generate URLs
def generate_url(year):
    return f"{BASE_URL}{year}.htm"


# function for processing the pre-2020 meeting date strings  into start and end dates
def process_date_string(date_string):
    """
    Convert a date string into start and end dates in yyyy-mm-dd format.

    Args:
    - date_string (str): The raw date string in the format 'month day year'.

    Returns:
    - tuple: A tuple of strings (start_date, end_date) in 'yyyy-mm-dd' format.
    """
    # Split the string into sections
    month_section, day_section, year = date_string.split(" ")

    # Handle month ranges (e.g., "Apr/May")
    if "/" in month_section:
        start_month, end_month = month_section.split("/")
    else:
        start_month = end_month = month_section

    # Handle day ranges (e.g., "30-31")
    if "-" in day_section:
        start_day, end_day = day_section.split("-")
    else:
        start_day = end_day = day_section

    # Combine into full date strings
    start_date_str = f"{start_day} {start_month} {year}"
    end_date_str = f"{end_day} {end_month} {year}"

    # Parse and format the dates
    start_date = parser.parse(start_date_str).strftime("%Y-%m-%d")
    end_date = parser.parse(end_date_str).strftime("%Y-%m-%d")

    return start_date, end_date

# Scrape FOMC dates for years before 2019
def scrape_fomc_dates(urls):

    # Initialize a list to store data
    data = []

    # Scrape data from each URL
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # extract the year from the current url
        match = re.search(r"(\d{4})", url)
        year = int(match.group(1))

        # handle the change of structure from 2011 onwards
        if year <= 2010:
            headings = soup.select('div.panel-heading')
        else: headings = soup.select('h5.panel-heading')

        for heading in headings:
            date_text = heading.get_text(strip=True)
            print(date_text)

            if "Meeting" in date_text:
                # Clean and process the date string
                parts = re.split(r"Meeting - ", date_text)
                if len(parts) == 2:
                    original_date_string = parts[0].strip() + " " + parts[1].strip()
                    try:
                        start_date, end_date = process_date_string(original_date_string)
                        data.append({
                            "raw_date_text": date_text,
                            "original_date_string": original_date_string,
                            "start_date": start_date,
                            "end_date": end_date,
                            "scheduled": True
                        })
                    except ValueError as e:
                        print(f"Error processing date: {original_date_string} - {e}")
            elif "(unscheduled)" in date_text:
                parts = re.split("(unscheduled) - ", date_text)
                if len(parts) == 2:
                    original_date_string = parts[0].strip() + " " + parts[1].strip()
                    try:
                        start_date, end_date = process_date_string(original_date_string)
                        data.append({
                            "raw_date_text": date_text,
                            "original_date_string": original_date_string,
                            "start_date": start_date,
                            "end_date": end_date,
                            "scheduled": False
                        })
                    except ValueError as e:
                        print(f"Error processing date: {original_date_string} - {e}")

    # Convert to DataFrame
    return pd.DataFrame(data)


# Scrape FOMC dates for 2020 and later
def scrape_post_2020(url):
    """
    Scrape FOMC meeting data for years after 2020, including start and end dates,
    and whether the meeting was scheduled or unscheduled.

    Args:
        url (str): URL to scrape.

    Returns:
        pd.DataFrame: DataFrame with columns "raw_date_text", "original_date_string",
                      "start_date", "end_date", and "scheduled".
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    panels = soup.select("div.panel.panel-default")
    records = []

    for panel in panels:
        # Extract year
        heading_text = panel.select_one("div.panel-heading").get_text(strip=True)
        year = heading_text.split(" FOMC")[0]

        # Extract months and days
        months = [m.get_text(strip=True) for m in panel.select("div.fomc-meeting__month")]
        days = [d.get_text(strip=True) for d in panel.select("div.fomc-meeting__date")]

        for month, day in zip(months, days):
            # Check if the day text contains "(unscheduled)"
            scheduled = "(unscheduled)" not in day
            day_cleaned = day.replace("(unscheduled)", "").replace("*", "").strip()

            # Handle single day or range of days
            if "-" in day_cleaned:
                start_day, end_day = day_cleaned.split("-")
            else:
                start_day = end_day = day_cleaned

            # Handle one month or split across months
            if "/" in month:
                start_month, end_month = month.split("/")
            else:
                start_month = end_month = month

            # Combine into full date strings
            start_date_str = f"{start_day} {start_month} {year}"
            end_date_str = f"{end_day} {end_month} {year}"

            # Convert to yyyy-mm-dd format
            try:
                start_date = parser.parse(start_date_str).strftime("%Y-%m-%d")
                end_date = parser.parse(end_date_str).strftime("%Y-%m-%d")

                # Append the data
                records.append({
                    "raw_date_text": heading_text,
                    "original_date_string": f"{start_date_str} - {end_date_str}",
                    "start_date": start_date,
                    "end_date": end_date,
                    "scheduled": scheduled
                })
            except ValueError:
                print(f"Error parsing date: {start_date_str} or {end_date_str}")

    # Create and return DataFrame
    return pd.DataFrame(records)


# Main function to orchestrate scraping and saving data
def main():
    # Generate URLs for years before 2020
    urls = [generate_url(year) for year in YEARS]
    print(urls)
    # Scrape data for years before 2020
    dates_pre_2020 = scrape_fomc_dates(urls)

    # Scrape data for 2020 and later
    dates_post_2020 = scrape_post_2020(POST_2013_URL)

    # Combine data and save to CSV
    calendar_data = pd.concat([dates_pre_2020, dates_post_2020], ignore_index=True)
    calendar_data.to_csv("FOMC_dates.csv", index=False)
    print("Data scraping complete. Saved to 'FOMC_dates.csv'.")


# Run the script if executed as the main module
if __name__ == "__main__":
    main()