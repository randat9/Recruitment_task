import requests
import pandas as pd
from datetime import datetime, timedelta
import schedule
import time
import os
import logging

class CurrencyDataLogger:
    def __init__(self, log_filename):
        logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

class CurrencyDataFetcher:
    def __init__(self, base_url="http://api.nbp.pl/api/exchangerates/rates/A/", currencies=None):
        if currencies is None:
            currencies = ["EUR/PLN", "USD/PLN", "CHF/PLN"]
        self.base_url = base_url
        self.currencies = currencies

    def fetch_data(self, start_date, end_date):
        data = pd.DataFrame()
        for currency in self.currencies:
            base, quote = currency.split('/')
            url = f"{self.base_url}{base}/{start_date}/{end_date}/?format=json"
            try:
                response = requests.get(url)
                response.raise_for_status()
                currency_data = response.json()
                rates = [rate['mid'] for rate in currency_data['rates']]
                dates = [rate['effectiveDate'] for rate in currency_data['rates']]
                temp_df = pd.DataFrame({'Date': dates, currency: rates})
                data = temp_df if data.empty else pd.merge(data, temp_df, on='Date')
            except requests.RequestException as e:
                logging.error(f"Error fetching data for {currency}: {e}")
                return None
        if not data.empty:
            data['EUR/USD'] = data['EUR/PLN'] / data['USD/PLN']
            data['CHF/USD'] = data['CHF/PLN'] / data['USD/PLN']
        return data

class DataSaver:
    @staticmethod
    def save(data, filename):
        try:
            data.to_csv(filename, index=False)
            logging.info(f"Data saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving data: {e}")

    @staticmethod
    def append_new_data_to_csv(new_data, filename):
        try:
            if os.path.exists(filename):
                existing_data = pd.read_csv(filename)
                combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset='Date', keep='last')
            else:
                combined_data = new_data
            combined_data.to_csv(filename, index=False)
        except Exception as e:
            logging.error(f"Error appending data: {e}")

class UserInterface:
    @staticmethod
    def prompt_for_date_range():
        format_str = '%Y-%m-%d'
        print("Enter the date range for which you want the data.")
        start_date_str = input("Enter start date (YYYY-MM-DD): ")
        end_date_str = input("Enter end date (YYYY-MM-DD): ")
        try:
            start_date = datetime.strptime(start_date_str, format_str)
            end_date = datetime.strptime(end_date_str, format_str)
            if start_date > end_date:
                raise ValueError("Start date must be before end date.")
            return start_date.strftime(format_str), end_date.strftime(format_str)
        except ValueError as e:
            print(f"Invalid date format or range: {e}")
            return None, None

    @staticmethod
    def prompt_for_currency_pairs(available_pairs):
        print("Available currency pairs:", ', '.join(available_pairs))
        selected_pairs = input("Enter the currency pairs you want to save (comma-separated): ").split(',')
        valid_pairs = [pair.strip() for pair in selected_pairs if pair.strip() in available_pairs]
        invalid_pairs = [pair.strip() for pair in selected_pairs if pair.strip() not in available_pairs]
        if invalid_pairs:
            logging.warning(f"Invalid currency pairs ignored: {', '.join(invalid_pairs)}")
        return valid_pairs

class CurrencyDataAnalyzer:
    @staticmethod
    def analyze_currency_pair(data, currency_pair):
        if currency_pair in data.columns:
            print(f"Analysis for {currency_pair}:")
            print("Average Rate:", data[currency_pair].mean())
            print("Median Rate:", data[currency_pair].median())
            print("Minimum Rate:", data[currency_pair].min())
            print("Maximum Rate:", data[currency_pair].max())
        else:
            print(f"{currency_pair} is not available in the data.")

class SchedulerTask:
    def __init__(self, fetcher, saver, filename):
        self.fetcher = fetcher
        self.saver = saver
        self.filename = filename

    def scheduled_task(self):
        try:
            today = datetime.today().strftime('%Y-%m-%d')
            start_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
            currency_data = self.fetcher.fetch_data(start_date, today)
            if currency_data is not None:
                self.saver.append_new_data_to_csv(currency_data, self.filename)
        except Exception as e:
            logging.error(f"An error occurred during scheduled task: {e}")

    def start_schedule(self):
        schedule.every().day.at("12:00").do(self.scheduled_task)

if __name__ == "__main__":
    logger = CurrencyDataLogger('currency_data_log.log')
    fetcher = CurrencyDataFetcher()
    saver = DataSaver()
    ui = UserInterface()
    analyzer = CurrencyDataAnalyzer()

    start_date, end_date = ui.prompt_for_date_range()
    if start_date and end_date:
        currency_data = fetcher.fetch_data(start_date, end_date)
        if currency_data is not None:
            saver.save(currency_data, 'all_currency_data.csv')
            selected_pairs = ui.prompt_for_currency_pairs(currency_data.columns[1:])
            filtered_data = currency_data[['Date'] + selected_pairs]
            saver.save(filtered_data, 'selected_currency_data.csv')
            pair_to_analyze = input("Enter the currency pair you want to analyze: ")
            analyzer.analyze_currency_pair(currency_data, pair_to_analyze)

    scheduler = SchedulerTask(fetcher, saver, 'all_currency_data.csv')
    scheduler.start_schedule()
