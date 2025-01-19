import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
from typing import List, Dict, Optional


class StockScraper:
    def __init__(self):
        self.base_url = 'https://www.mse.mk/en/stats/symbolhistory/'
        self.data_dir = './data'
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_companies(self) -> List[str]:
        """Fetch list of available companies."""
        sample_url = f'{self.base_url}KMB'
        response = requests.get(sample_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        company_names = soup.select('.form-control option')

        return [
            name.text for name in company_names
            if not any(char.isdigit() for char in name.text)
        ]

    def parse_cells(self, row) -> Dict:
        """Parse table row cells into structured data."""
        cells = row.find_all('td')

        def format_price(value: str) -> str:
            try:
                return "{:,.2f}".format(float(value.replace(',', '.'))).replace(
                    ',', 'X').replace('.', ',').replace('X', '.')
            except ValueError:
                return value

        return {
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

    def scrape_data_from_url(
            self,
            company: str,
            date_from: str,
            date_to: str,
            retries: int = 3
    ) -> pd.DataFrame:
        """Scrape data for a specific company and date range."""
        url = f"{self.base_url}{company}?FromDate={date_from}&ToDate={date_to}"

        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=(30, 120))
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    rows = soup.find_all('tbody')[0].find_all('tr') if soup.find_all('tbody') else []
                    data = [self.parse_cells(row) for row in rows]
                    return pd.DataFrame(data)
                else:
                    print(f"Failed to fetch data for {company}: HTTP {response.status_code}")
                    return pd.DataFrame()
            except requests.exceptions.ReadTimeout:
                print(f"Timeout occurred for {company}. Retrying ({attempt + 1}/{retries})...")
                time.sleep(2 ** attempt)

        print(f"Failed to fetch data for {company} after {retries} retries")
        return pd.DataFrame()

    def fetch_data_for_company(
            self,
            company: str,
            years_back: int = 10
    ) -> Optional[str]:
        """Fetch historical data for a single company."""
        today = datetime.today()

        company_data = []
        for year in range(years_back):
            date_to = today - timedelta(days=365 * year)
            date_from = today - timedelta(days=365 * (year + 1))

            date_to_str = date_to.strftime("%m/%d/%Y")
            date_from_str = date_from.strftime("%m/%d/%Y")

            yearly_data = self.scrape_data_from_url(company, date_from_str, date_to_str)
            if not yearly_data.empty:
                company_data.append(yearly_data)

        if company_data:
            final_df = pd.concat(company_data, ignore_index=True)
            output_path = os.path.join(self.data_dir, f'{company}.csv')
            final_df.to_csv(output_path, index=False)
            return output_path

        return None

    def fetch_all_companies_data(self, years_back: int = 10) -> Dict[str, str]:
        """Fetch data for all companies using multiple threads."""
        companies = self.fetch_companies()
        results = {}

        def worker(company: str) -> tuple:
            try:
                output_path = self.fetch_data_for_company(company, years_back)
                return company, output_path
            except Exception as e:
                print(f"Error while fetching data for {company}: {e}")
                return company, None

        max_threads = 10
        with ThreadPoolExecutor(max_threads) as executor:
            futures = [executor.submit(worker, company) for company in companies]
            for future in as_completed(futures):
                company, path = future.result()
                if path:
                    results[company] = path

        return results