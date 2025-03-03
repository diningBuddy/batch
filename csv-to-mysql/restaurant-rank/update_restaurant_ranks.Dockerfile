FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# 필요한 파일 복사
COPY restaurant-rank/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright 설치 및 Chromium 브라우저 다운로드
RUN playwright install chromium

# 애플리케이션 파일 복사
COPY restaurant-rank/kakao_restaurants.csv .
COPY restaurant-rank/kakao_rank.py .
COPY restaurant-rank/update_restaurant_ranks.py .
COPY restaurant-rank/run.py .

# 기존 데이터 파일 복사 (선택사항)
COPY restaurant-rank/kakao_map_ranks.csv .

# 환경 변수 설정
ENV MYSQL_HOST=mysql \
    MYSQL_PORT=3306 \
    MYSQL_USER=skku-user \
    MYSQL_PASSWORD=skku-pw \
    MYSQL_DB=skku

# 실행 명령
CMD ["python", "run.py"]
