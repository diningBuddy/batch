FROM python:3.8-slim

WORKDIR /app

COPY update_restaurant_ranks.py /app/insert_restaurant_ranks.py
COPY ./kakao_map_ranks.csv /app/kakao_map_ranks.csv

RUN pip install pymysql csv os

CMD ["python", "update_restaurant_ranks.py"]
