FROM python:3.8-slim

ARG TARGETARCH

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && if [ "$TARGETARCH" = "amd64" ]; then \
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
        apt-get update && \
        apt-get install -y google-chrome-stable; \
    else \
        apt-get update && \
        apt-get install -y chromium-chromedriver; \
    fi \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 필요한 파일 복사
COPY restaurant-rank/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY restaurant-rank/kakao_restaurants.csv .
COPY restaurant-rank/kakao_rank.py .
COPY restaurant-rank/update_restaurant_ranks.py .
COPY restaurant-rank/run.py .

# 기존 데이터 파일 복사 (선택사항 - 크롤링 실패 시 백업용)
COPY restaurant-rank/kakao_map_ranks.csv .

# 환경 변수 설정
ENV MYSQL_HOST=mysql \
    MYSQL_PORT=3306 \
    MYSQL_USER=skku-user \
    MYSQL_PASSWORD=skku-pw \
    MYSQL_DB=skku

# 실행 명령
CMD ["python", "run.py"]