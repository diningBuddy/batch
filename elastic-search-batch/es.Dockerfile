FROM python:3.8-slim

COPY es-requirements.txt es-requirements.txt
COPY ../csv/restaurants.csv restaurants.csv
COPY csv-to-es.py csv-to-es.py
COPY ../csv/menus.csv menus.csv

RUN pip install -r es-requirements.txt

ENTRYPOINT ["python3", "csv-to-es.py"]