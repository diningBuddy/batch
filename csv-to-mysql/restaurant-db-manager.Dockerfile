# Python 베이스 이미지 사용
FROM python:3.8-slim

# 작업 디렉토리 설정
WORKDIR /app

# 스크립트 복사
COPY ./restaurant_db_manager.py /app/restaurant_db_manager.py
COPY ./kakao_categories.txt /app/kakao_categories.txt
COPY ./kakao_menus.csv /app/kakao_menus.csv
COPY ./kakao_restaurants.csv /app/kakao_restaurants.csv
COPY ./insert_menus.py /app/insert_menus.py
COPY ./insert_restaurants.py /app/insert_restaurants.py
COPY ./insert_category_mapping.py /app/insert_category_mapping.py
COPY ./insert_categories.py /app/insert_categories.py
COPY ./update_restaurants_menus.py /app/update_restaurants_menus.py

# MySQL 클라이언트 라이브러리 설치
RUN pip install pymysql cryptography

# MySQL 데이터 삽입 스크립트 실행
CMD ["python", "restaurant_db_manager.py"]
