import time
import threading
import re
import time
import signal
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from accounting_sender import AccountingSender

stop_monitoring = False

chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--remote-debugging-port=9222')

# Define a set to store unique cache entries
cache_set = set()

# Initialize Chrome WebDriver
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.banking-oberbank.at")

# classes:
# obk financial-overview d/content/
def scrape_account_details(html_doc):
    soup = BeautifulSoup(html_doc, features="html.parser")
    divs = soup.find_all('div', class_='column-wrapper vp')
    for div in divs:
        dates = div.find_all('div', class_='trigger')
        if len(dates) > 0:
            transaction_date =  dates[0].get_text(strip=True)
            booking_date = dates[1].get_text(strip=True)
            comment =  dates[2].get_text(strip=True)
            amount_str = div.find('span', class_='no-wrap').get_text(strip=True)
            # Replace unwanted characters with empty string
            clean_amount_str = re.sub(r'[^\d,-]', '', amount_str)
            # Replace comma with dot for proper float conversion
            clean_amount_str = clean_amount_str.replace(',', '.')
            # Convert the cleaned string to float
            amount = float(clean_amount_str)
            # Store the extracted data in a cache (dictionary)
            cache_entry = {
                'transaction_date': transaction_date,
                'date': booking_date,
                'reference': comment,
                'amount': amount
            }
            if frozenset(cache_entry.items()) not in cache_set:
                print(cache_entry)
            cache_set.add(frozenset(cache_entry.items()))

# Function to scrape a single site
def scrape_account_overview(html_doc):
    if html_doc:
        soup = BeautifulSoup(html_doc, features="html.parser")
    
        tr_element = soup.findAll('tr', class_='db-trow js-turnover-link db-last-transactions-table-row')
        for ele in tr_element:

            try:
            # Extract specific data from the <tr> element
            # 1. Extract dates from the first two <td> elements
                dates_elements = ele.find_all('td', class_='db-tcol')
                transaction_date = dates_elements[0].get_text(strip=True)
                booking_date = dates_elements[1].get_text(strip=True)
                comment =  dates_elements[2].get_text(strip=True)
                # remove unwanted currency and special char, cleanup and format into number
                amount_str = dates_elements[3].get_text(strip=True) #"-60,00\xa0EUR"
                # Replace unwanted characters with empty string
                clean_amount_str = re.sub(r'[^\d,-]', '', amount_str)
                # Replace comma with dot for proper float conversion
                clean_amount_str = clean_amount_str.replace(',', '.')
                # Convert the cleaned string to float
                amount = float(clean_amount_str)
                # Store the extracted data in a cache (dictionary)
                cache_entry = {
                    'transaction_date': transaction_date,
                    'date': booking_date,
                    #'name': name,
                    #'cleaned_time': cleaned_time,
                    'reference': comment,
                    'amount': amount
                }

                cache_set.add(frozenset(cache_entry.items()))

            except Exception as e:
                print("Error: ", e)

# Function to monitor the user's browsing activity
def monitor_browsing():

    # Monitor the user's browsing activity
    while not stop_monitoring:
        # Get the current URL the user is visiting
        if driver:
            current_url = driver.current_url

        # Check if the URL has changed since the last check
        # You may need to implement additional logic here to avoid scraping the same URL multiple times
        if "https://www.banking-oberbank.at/group/oberbank/finanzen" in current_url:
            html_doc=driver.page_source
            # Scraping logic
            threading.Thread(target=scrape_account_overview, args=(html_doc,)).start()
        elif "banking-oberbank.at/group/oberbank/accountdetails" in current_url:
            html_doc=driver.page_source
            # Scraping logic
#            scrape_site(html_doc)
            threading.Thread(target=scrape_account_details, args=(html_doc,)).start()
        # Check every 5 seconds
        time.sleep(0.5)


def signal_handler(sig, frame):
    stop_monitoring = True
    driver.quit()
    base_url = "http://0.0.0.0:5000"
    accounting_sender = AccountingSender(base_url)

    print("\nCtrl+C detected. Persisting cache..")
    # Perform cleanup actions here
    # For example: Close connections, save data, etc.
    accounting_sender.send_accounting_data(cache_set)
    sys.exit(0)


# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# Start monitoring the user's browsing activity in a separate thread
threading.Thread(target=monitor_browsing).start()


# Keep the main thread running to keep the browser window open
while True:
    time.sleep(1)
