# Python 3.9 이미지 사용
FROM python:3.9

# 작업 디렉토리 설정
WORKDIR /opt/src

# 필요한 패키지 설치
RUN pip install --no-cache-dir \
    google-cloud-storage \
    yfinance \
    pandas \
    requests \
    beautifulsoup4

# 소스 코드 복사
COPY . .

# 컨테이너 실행 시 기본 명령어
# CMD ["python", "/opt/src/data_collection/short_term/fetch_stock_data.py"]
