FROM python:3.8-slim

COPY requirements.txt requirements.txt
COPY restaurants.csv restaurants.csv
COPY menus.csv menus.csv
COPY main.py main.py

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]