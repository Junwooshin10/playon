import gspread
import pandas as pd

SERVICE_ACCOUNT_FILE = 'service-account.json'
SHEET_NAME = 'Search_Result'
csv_dir = 'docs/'
gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)

# 데이터 가져오기 함수
def fetch_csv_data(sheet_name):
    df = pd.read_csv(csv_dir+sheet_name+'_data.csv')
    return df

def fetch_sheet_data_to_csv(sheet_name):
    """스프레드시트의 특정 워크시트 데이터를 가져옵니다."""
    wks = gc.open(SHEET_NAME).worksheet(sheet_name)
    records = wks.get_all_records()
    df = pd.DataFrame(records)
    df.to_csv(path_or_buf=csv_dir+sheet_name+'_data.csv')
    return df