# Python 베이스 이미지 사용
FROM python:3.8-slim

# 작업 디렉토리 설정
WORKDIR /app

# 스크립트 복사
COPY ./create-tables.py /app/create-tables.py

# MySQL 클라이언트 라이브러리 설치
RUN pip install pymysql cryptography

# MySQL 테이블 생성 스크립트 실행
CMD ["python", "create-tables.py"]
