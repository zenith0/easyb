import time
import threading
import re
import time
import signal
import sys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from accounting_sender import AccountingSender
from dotenv import load_dotenv
import os
from webdriver_manager.chrome import ChromeDriverManager 
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService

# Load variables from .env file
load_dotenv()


# Access environment variables
DISPOSER = os.getenv('DISPOSER')
PIN = os.getenv('PIN')
ACCOUNT_ID = os.getenv('ACCOUNT_ID')


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
service=ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(options=chrome_options, service=service)

print("Still alive")

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
    try:
    # Monitor the user's browsing activity
        while not stop_monitoring:
            # Get the current URL the user is visiting
            if driver:
                current_url = driver.current_url

        # Check if the URL has changed since the last check
        # You may need to implement additional logic here to avoid scraping the same URL multiple times
            if "banking-oberbank.at/group/oberbank/accountdetails" in current_url:
                html_doc=driver.page_source
            # Scraping logic
#            scrape_site(html_doc)
                threading.Thread(target=scrape_account_details, args=(html_doc,)).start()
        # Check every 5 seconds
            time.sleep(0.5)
    except Exception as e:
        print("Error, ", str(e))


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

wait = WebDriverWait(driver, 10)

def login_to_details_view(driver):
    try:
    # Wait for the username input field to be visible
        username_input = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "loginDisposer")))
        username_input.send_keys(DISPOSER)
        password_input = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "loginPin")))
        password_input.send_keys(PIN)
        password_input.send_keys(Keys.ENTER)

    except TimeoutException:
        print("Timeout occurred while waiting for element to be clickable.")
    # Handle the timeout situation here
    except Exception as e:
        print("An error occurred:", e)

def navigate_to_details(driver):
    amount_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'db-amount'))
        )
    amount_element.click()

            # Find the <span class="vc"> element containing the account number and wait for it to be clickable
    account_number_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(@class, "vc")]/span[contains(@class, "edit-visible")]'))
        )
    account_number_element.click()

        # Wait for the element to be clickable
    element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Zur Umsatzübersicht']"))
        )
    element.click()

        # Wait for the element to be clickable
    element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@for='more-turnovers' and contains(text(), 'Weitere Umsätze anzeigen')]"))
        )
    element.click()

def main():
    # Register the signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)
    
    driver.get("https://www.banking-oberbank.at")
    # login and navigate to the account details
    # Find the username input field and fill it out
    login_to_details_view(driver)
    driver.get("https://www.banking-oberbank.at/group/oberbank/accountdetails?accountID="+ACCOUNT_ID)
    # Start monitoring the user's browsing activity in a separate thread
    threading.Thread(target=monitor_browsing).start()

    # Keep the main thread running to keep the browser window open
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()