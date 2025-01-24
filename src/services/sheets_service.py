import gspread
import pandas as pd

SERVICE_ACCOUNT_FILE = 'service-account.json'
SHEET_NAME = 'Search_Result'
csv_dir = 'docs/'
gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)

# Function to fetch data
def fetch_csv_data(sheet_name):
    df = pd.read_csv(csv_dir + sheet_name + '_data.csv')
    return df

def fetch_sheet_data_to_csv(sheet_name):
    """Fetch data from a specific worksheet in the spreadsheet."""
    wks = gc.open(SHEET_NAME).worksheet(sheet_name)
    records = wks.get_all_records()
    df = pd.DataFrame(records)
    df.to_csv(path_or_buf=csv_dir + sheet_name + '_data.csv')
    return df