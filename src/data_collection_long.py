import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 크롤링 대상 URL
URL = "https://www.finhacker.cz/top-20-sp-500-companies-by-market-cap/"

# 웹 페이지 요청
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
response = requests.get(URL, headers=headers)

# 요청 성공 확인
if response.status_code != 200:
    print(f"❌ 요청 실패: {response.status_code}")
    exit()

# HTML 파싱
soup = BeautifulSoup(response.text, "html.parser")

# 연도별 데이터 저장
yearly_companies = {}

# 크롤링할 연도 (1989년부터 최신까지)
years = [str(year) for year in range(1989, 2027)]

# 연도별 데이터 크롤링
for year in years:
    section = soup.find("section", {"id": f"{year}y"})

    if not section:
        print(f"❌ {year}년 데이터 없음")
        continue

    companies = []

    # 각 회사 정보가 담긴 태그 찾기
    for company_div in section.find_all("div", class_="bar"):
        title = company_div.get("title")  # title 속성에서 회사명 추출
        if title:
            company_name = title.split(". ")[-1]  # "1. Exxon Mobil" -> "Exxon Mobil"
            companies.append(company_name)

    yearly_companies[year] = companies
    print(f"✅ {year}년 데이터 수집 완료: {companies}")

    time.sleep(1)  # 너무 빠른 요청 방지

# 데이터프레임 변환
df = pd.DataFrame.from_dict(yearly_companies, orient="index").transpose()

# CSV 저장
df.to_csv("data/long_term/long_term_top20_names.csv", index=False, encoding="utf-8-sig")

print("✅ 모든 연도 데이터 저장 완료!")
