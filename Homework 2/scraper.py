import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep


def format_date(date):
    return date.strftime("%m/%d/%Y")


def init_directory():
    if not os.path.exists('./data'):
        os.makedirs('./data')


BASE_URL = 'https://www.mse.mk/en/stats/symbolhistory/'
init_directory()


def fetch_companies():
    sample_url = 'https://www.mse.mk/en/stats/symbolhistory/KMB'
    response = requests.get(sample_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    company_names = soup.select('.form-control option')

    valid_company_names = [name.text for name in company_names if not any(char.isdigit() for char in name.text)]
    return valid_company_names


companies = fetch_companies()


def parse_cells(row):
    cells = row.find_all('td')

    def format_price(value):
        try:
            return "{:,.2f}".format(float(value.replace(',', '.'))).replace(',', 'X').replace('.', ',').replace('X',
                                                                                                                '.')
        except ValueError:
            return value

    item = {
        'Date': cells[0].text,
        'Last trade price': format_price(cells[1].text),
        'Max': format_price(cells[2].text),
        'Min': format_price(cells[3].text),
        'Avg Price': format_price(cells[4].text),
        '%chg.': cells[5].text.replace('.', ','),
        'Volume': cells[6].text,
        'TurnoverBEST_MKD': format_price(cells[7].text),
        'TotalTurnoverMKD': format_price(cells[8].text)
    }

    return item


def scrape_data_from_url(company, date_from, date_to, retries=3):
    url = f"{BASE_URL}{company}?FromDate={date_from}&ToDate={date_to}"
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=(30, 120))
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                rows = soup.find_all('tbody')[0].find_all('tr') if soup.find_all('tbody') else []
                data = [parse_cells(row) for row in rows]
                return pd.DataFrame(data)
            else:
                print(f"Failed to fetch data for {company}: HTTP {response.status_code}")
                return pd.DataFrame()
        except requests.exceptions.ReadTimeout:
            print(f"Timeout occurred for {company}. Retrying ({attempt + 1}/{retries})...")
            sleep(2 ** attempt)
    print(f"Failed to fetch data for {company} after {retries} retries")
    return pd.DataFrame()


def fetch_data_for_company(company, years_back=10):
    today = datetime.today()
    end_date = format_date(today)
    start_date = format_date(today - timedelta(days=365 * years_back))

    company_data = []
    for year in range(years_back):
        date_to = format_date(today - timedelta(days=365 * year))
        date_from = format_date(today - timedelta(days=365 * (year + 1)))

        yearly_data = scrape_data_from_url(company, date_from, date_to)
        if not yearly_data.empty:
            company_data.append(yearly_data)

    if company_data:
        final_df = pd.concat(company_data, ignore_index=True)
        final_df.to_csv(f'./data/{company}.csv', index=False)
        print(f"Data for {company} saved to ./data/{company}.csv")
    else:
        print(f"No data collected for {company}")


def fetch_data_for_all_companies_threaded(years_back=10):
    start_time = time.time()

    def worker(company):
        try:
            print(f"Fetching data for {company}")
            fetch_data_for_company(company, years_back)
        except Exception as e:
            print(f"Error while fetching data for {company}: {e}")
        sleep(2)

    max_threads = 10
    with ThreadPoolExecutor(max_threads) as executor:
        futures = [executor.submit(worker, company) for company in companies]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Unhandled exception: {e}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total time taken to fetch data: {elapsed_time / 60:.2f} minutes")


fetch_data_for_all_companies_threaded()