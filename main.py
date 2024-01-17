import requests
import pandas as pd
from datetime import datetime, timedelta
import schedule
import time
import os
import logging

# Configure logging
logging.basicConfig(filename='currency_data_log.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def fetch_currency_data():
    """
    Fetches currency data for a predefined list of currency pairs over the last 90 days.
    Returns a DataFrame with the fetched data or None if an error occurs.
    """
    base_url = "http://api.nbp.pl/api/exchangerates/rates/A/"
    currencies = ["EUR/PLN", "USD/PLN", "CHF/PLN"]
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')

    data = pd.DataFrame()

    for currency in currencies:
        base, quote = currency.split('/')
        url = f"{base_url}{base}/{start_date}/{end_date}/?format=json"

        try:
            response = requests.get(url)
            response.raise_for_status()
            currency_data = response.json()

            rates = [rate['mid'] for rate in currency_data['rates']]
            dates = [rate['effectiveDate'] for rate in currency_data['rates']]

            temp_df = pd.DataFrame({'Date': dates, currency: rates})
            data = temp_df if data.empty else pd.merge(data, temp_df, on='Date')

        except requests.HTTPError as e:
            logging.error(f"HTTP error fetching data for {currency}: {e}")
            return None
        except requests.ConnectionError as e:
            logging.error(f"Connection error fetching data for {currency}: {e}")
            return None
        except requests.Timeout as e:
            logging.error(f"Timeout error fetching data for {currency}: {e}")
            return None
        except requests.RequestException as e:
            logging.error(f"Error fetching data for {currency}: {e}")
            return None

    if not data.empty:
        data['EUR/USD'] = data['EUR/PLN'] / data['USD/PLN']
        data['CHF/USD'] = data['CHF/PLN'] / data['USD/PLN']
    return data
def save_data(data, filename):
    """
    Saves the provided data to a CSV file.
    Parameters:
    - data: DataFrame containing the data to be saved.
    - filename: String representing the name of the file where data will be saved.
    """
    try:
        data.to_csv(filename, index=False)
        logging.info(f"Data saved to {filename}")
    except Exception as e:
        logging.error(f"Error saving data: {e}")

def validate_currency_pairs(input_pairs, available_pairs):
    """
    Validates user input for currency pairs against available pairs.
    Parameters:
    - input_pairs: List of strings representing user input currency pairs.
    - available_pairs: List of strings representing available currency pairs.
    Returns a list of valid currency pairs.
    """
    valid_pairs = [pair.strip() for pair in input_pairs if pair.strip() in available_pairs]
    invalid_pairs = [pair.strip() for pair in input_pairs if pair.strip() not in available_pairs]
    if invalid_pairs:
        logging.warning(f"Invalid currency pairs ignored: {', '.join(invalid_pairs)}")
    return valid_pairs

def select_and_save_data(data):
    """
    Prompts the user to select currency pairs to save and saves the selected data.
    Parameter:
    - data: DataFrame containing currency data.
    """
    available_pairs = list(data.columns[1:])
    print("Available currency pairs:", ', '.join(available_pairs))
    selected_pairs = input("Enter the currency pairs you want to save (comma-separated): ").split(',')
    valid_selected_pairs = validate_currency_pairs(selected_pairs, available_pairs)

    if valid_selected_pairs:
        filtered_data = data[['Date'] + valid_selected_pairs]
        save_data(filtered_data, 'selected_currency_data.csv')
    else:
        print("No valid currency pairs selected. No data saved.")

def analyze_currency_pair(data, currency_pair):
    """
    Performs basic analysis on the specified currency pair.
    Parameters:
    - data: DataFrame containing currency data.
    - currency_pair: String representing the currency pair to analyze.
    """
    if currency_pair in data.columns:
        print(f"Analysis for {currency_pair}:")
        print("Average Rate:", data[currency_pair].mean())
        print("Median Rate:", data[currency_pair].median())
        print("Minimum Rate:", data[currency_pair].min())
        print("Maximum Rate:", data[currency_pair].max())
    else:
        print(f"{currency_pair} is not available in the data.")


#### Append New Data to CSV Function

def append_new_data_to_csv(new_data, filename):
    """
    Appends new data to an existing CSV file or creates a new one if it doesn't exist.
    Parameters:
    - new_data: DataFrame containing the new data to append.
    - filename: String representing the name of the file.
    """
    try:
        if os.path.exists(filename):
            existing_data = pd.read_csv(filename)
            combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset='Date', keep='last')
        else:
            combined_data = new_data
        combined_data.to_csv(filename, index=False)
    except Exception as e:
        logging.error(f"Error appending data: {e}")

def scheduled_task():
    """
    Scheduled task to fetch new currency data and append it to a CSV file.
    """
    try:
        currency_data = fetch_currency_data()
        if currency_data is not None:
            append_new_data_to_csv(currency_data, 'all_currency_data.csv')
    except Exception as e:
        logging.error(f"An error occurred during scheduled task: {e}")

# Schedule the task
schedule.every().day.at("12:00").do(scheduled_task)

if __name__ == "__main__":
    try:
        currency_data = fetch_currency_data()
        if currency_data is not None:
            save_data(currency_data, 'all_currency_data.csv')
            select_and_save_data(currency_data)
            pair_to_analyze = input("Enter the currency pair you want to analyze: ")
            analyze_currency_pair(currency_data, pair_to_analyze)
    except Exception as e:
        logging.error(f"An error occurred in main execution: {e}")

    # Infinite loop for scheduled task with graceful exit
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Script stopped by user.")



