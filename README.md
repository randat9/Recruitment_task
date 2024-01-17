# Recruitment_task
Currency Data Analysis

## Project Description
A tool for analyzing and tracking EUR/PLN, USD/PLN and CHF/PLN exchange rates, using National Bank of Poland API data. It allows downloading data from the last 90 days, calculating EUR/USD and CHF/USD rates and saving this information to CSV files. It also includes functionality to automatically update the data every day at 12:00 pm.

## Functionalities
- Downloading currency data from the last 90 days.
- Calculation and analysis of EUR/USD and CHF/USD exchange rates.
- Saving of data to CSV files.
- Automatic daily updates.
## Technologies
Python 3.8+

Libraries: Pandas, Requests
## Installing and Running
git clone https://github.com/twoje-repo/CurrencyDataAnalysis.git

cd CurrencyDataAnalysis

python script.py
## Usage Example
### Downloading Currency Data

Running the script will start the process of downloading EUR/PLN, USD/PLN, CHF/PLN currency data for the last 90 days from the National Bank of Poland. This data will be processed and additional EUR/USD and CHF/USD rates will be calculated.

### Selecting Currency Pairs for Analysis.

You can select the currency pairs you are interested in for analysis. For example, if you want to see data only for EUR/PLN and USD/PLN, just enter them when the script requests it

### Saving Selected Data
Once you have selected the currency pairs, the script will save this data to the selected_currency_data.csv file.

### Analyzing a Specific Currency Pair.
You can also perform a simple analysis for the selected currency pair. The script will display the average rate, median, minimum, and maximum for the selected pair.

### Automatic Updates
The script is programmed to run every day at 12:00 PM, automatically updating and saving the latest data to the all_currency_data.csv file. This ensures that you always have access to up-to-date currency exchange rate information.

### Error Handling
In case of problems, such as API connection errors, the script will log these errors, allowing you to easily track and resolve issues.


## Planned Expansions
- Adding more currency pairs.
- Expansion of analysis to include other financial indicators.
- Collaboration and Contribution
- Information on how to report bugs, feature suggestions and how to send pull requests is welcome.
- Adding visualizations



## Authors 
Adrian Oleś
