import gspread
import pandas as pd

SERVICE_ACCOUNT_FILE = 'service-account.json'
SHEET_NAME = 'Search_Result'
gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)

def fetch_injury_types_from_sheet():
    """
    gspread를 통해 'Search_Result' 스프레드시트 중 '부상종류' 워크시트에 있는 데이터를 가져옵니다.
    반환: [{'부상명': ..., '스포츠': ...}, ...] 형태의 리스트
    """
    wks = gc.open(SHEET_NAME).worksheet('부상종류')
    # 워크시트의 모든 기록(첫 행 헤더로 자동 인식)
    records = wks.get_all_records()
    return records

def fetch_sports_types_from_sheet():
    wks = gc.open(SHEET_NAME).worksheet('운동종류')
    records = wks.get_all_records()
    return records


def fetch_body_parts_from_sheet():
    """ '부상부위' 워크시트 데이터를 가져옵니다. """
    wks = gc.open(SHEET_NAME).worksheet('부상부위')
    body_parts = wks.col_values(1)[1:]  # 첫 번째 열에서 헤더를 제외하고 가져오기
    return body_parts

# 데이터 가져오기 함수
def fetch_sheet_data(sheet_name):
    """스프레드시트의 특정 워크시트 데이터를 가져옵니다."""
    wks = gc.open(SHEET_NAME).worksheet(sheet_name)
    records = wks.get_all_records()
    return pd.DataFrame(records)
