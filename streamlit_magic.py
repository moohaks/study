import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# 웹페이지 제목 설정
st.title('조엘 그린블라트의 마법공식')

# 버튼 생성
if st.button('실행'):
    # 기본 URL 설정
    base_url = "https://finance.naver.com/sise/sise_market_sum.naver?sosok=0&page="

    # 데이터를 저장할 리스트
    all_data = []

    # 1페이지부터 45페이지까지 반복
    for page in range(1, 46):
        # 각 페이지의 URL
        url = base_url + str(page)

        # HTTP GET 요청을 보내고 페이지 가져오기
        response = requests.get(url)
        response.encoding = 'euc-kr'  # 네이버 금융 페이지의 인코딩이 euc-kr이므로 설정 필요
        html = response.text

        # BeautifulSoup을 이용해 HTML 파싱
        soup = BeautifulSoup(html, 'html.parser')

        # 테이블에서 데이터 추출
        table = soup.find('table', {'class': 'type_2'})
        rows = table.find_all('tr')[2:]  # 첫 2개 행은 헤더이므로 제외

        # 각 행에서 데이터 추출
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 1:  # 빈 행은 제외
                data = [col.get_text().strip() for col in cols]
                all_data.append(data)

    # 데이터를 DataFrame으로 변환
    columns = ['N', '종목명', '현재가', '전일비', '등락률', '액면가', '시가총액', '상장주식수', '외국인비율', '거래량', 'PER', 'ROE', '토론실']
    df = pd.DataFrame(all_data, columns=columns)

    # '종목명', '현재가', '시가총액', 'PER', 'ROE' 컬럼만 선택
    selected_columns = df[['종목명', '현재가', '시가총액', 'PER', 'ROE']]

    # 숫자로 변환하기 위해 쉼표 제거 및 공백 처리
    selected_columns['현재가'] = selected_columns['현재가'].str.replace(',', '').astype(float)
    selected_columns['시가총액'] = selected_columns['시가총액'].str.replace(',', '').astype(float)
    selected_columns['PER'] = pd.to_numeric(selected_columns['PER'].str.replace(',', ''), errors='coerce')
    selected_columns['ROE'] = pd.to_numeric(selected_columns['ROE'].str.replace(',', ''), errors='coerce')

    # 'PER'와 'ROE' 컬럼에 NaN 값이 있는 행을 삭제
    selected_columns = selected_columns.dropna(subset=['PER', 'ROE'])

    # 'PER'와 'ROE' 컬럼에서 음수 값이 있는 행을 삭제
    selected_columns = selected_columns[(selected_columns['PER'] >= 0) & (selected_columns['ROE'] >= 0)]

    # 'PER' 오름차순으로 순위 부여
    selected_columns['PER 순위'] = selected_columns['PER'].rank(method='min', ascending=True)

    # 'ROE' 내림차순으로 순위 부여
    selected_columns['ROE 순위'] = selected_columns['ROE'].rank(method='min', ascending=False)

    # 'PER 순위'와 'ROE 순위'의 값을 더해서 'MAGIC SUM' 컬럼에 넣기
    selected_columns['MAGIC SUM'] = selected_columns['PER 순위'] + selected_columns['ROE 순위']

    # 'MAGIC SUM' 오름차순으로 순위 부여
    selected_columns['MAGIC 순위'] = selected_columns['MAGIC SUM'].rank(method='min', ascending=True)

    # 'MAGIC 순위' 기준 오름차순으로 정렬
    selected_columns_sorted = selected_columns.sort_values(by='MAGIC 순위', ascending=True)

    # 결과를 웹페이지에 출력
    st.dataframe(selected_columns_sorted)