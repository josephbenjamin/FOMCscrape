# FOMCscrape
Scrapes the FED-website for the dates of the Federal Open Market Committee

## What is the FOMC?
Find out here: https://www.federalreserve.gov/monetarypolicy/fomc.htm

## When does the FOMC meet?
The Federal Reserve makes currently makes available its schedule on this webpage
https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm


## How does FOMCscrape work?
- This webscraper has two key functions which act separately to:
  1. **scrape_fomc_dates**: scrape data from 1940 to 2012
    - This data is availabe from the historical page provided for each year to 2012
  2. **scrape_post_2013**: scrape data from 2013 onwards
    - This data is available at the fomccalendars page