FROM python:3.8-slim

COPY mysql-to-es-requirements.txt mysql-to-es-requirements.txt
COPY mysql-to-es.py mysql-to-es.py

RUN pip install -r mysql-to-es-requirements.txt

ENTRYPOINT ["python3", "mysql-to-es.py"]