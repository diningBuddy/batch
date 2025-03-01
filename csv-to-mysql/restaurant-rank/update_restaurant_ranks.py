import pymysql
import csv
import os
import logging
import sys

# 로깅 설정 (run.py에서 이미 설정했으므로 중복 방지)
logger = logging.getLogger(__name__)

def insert_ranks(db_config, csv_file_path):
  logger.info(f"DB 적재 시작: {csv_file_path}, 연결: {db_config['host']}")

  connection = pymysql.connect(**db_config)
  cursor = connection.cursor()

  updated_count = 0
  inserted_count = 0
  not_found_count = 0
  error_count = 0

  try:
    # 파일 존재 확인
    if not os.path.exists(csv_file_path):
      logger.error(f"Error: File '{csv_file_path}' not found.")
      return

    # CSV 파일 읽기
    with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
      reader = csv.DictReader(csvfile)
      total_rows = sum(1 for _ in reader)

      # 파일 포인터를 다시 처음으로
      csvfile.seek(0)
      next(csv.DictReader(csvfile))  # 헤더 건너뛰기

      logger.info(f"처리할 레코드: {total_rows}개")

      for row in reader:
        try:
          # 레스토랑 찾기
          find_restaurant_query = """
                    SELECT id FROM restaurants 
                    WHERE name = %s AND 
                          ABS(latitude - %s) < 0.0001 AND 
                          ABS(longitude - %s) < 0.0001
                    LIMIT 1
                    """

          cursor.execute(find_restaurant_query, (
            row['name'],
            float(row['lat']),
            float(row['lon'])
          ))

          result = cursor.fetchone()

          if result:
            restaurant_id = result[0]
            rank_number = int(row['rank'])

            # 존재 여부 확인
            check_query = """
                        SELECT id FROM restaurant_ranks WHERE restaurant_id = %s
                        """
            cursor.execute(check_query, (restaurant_id,))

            if cursor.fetchone():
              # 이미 존재하면 UPDATE
              update_query = """
                            UPDATE restaurant_ranks SET rank_number = %s 
                            WHERE restaurant_id = %s
                            """
              cursor.execute(update_query, (rank_number, restaurant_id))
              updated_count += 1
            else:
              # 없으면 INSERT
              insert_query = """
                            INSERT INTO restaurant_ranks (restaurant_id, rank_number)
                            VALUES (%s, %s)
                            """
              cursor.execute(insert_query, (restaurant_id, rank_number))
              inserted_count += 1

          else:
            not_found_count += 1
            logger.warning(f"레스토랑 '{row['name']}' 매칭 실패")

        except Exception as e:
          error_count += 1
          logger.error(f"Error processing row {row}: {e}")

      # 모든 처리가 끝난 후 커밋
      connection.commit()
      logger.info(f"DB 적재 결과: 삽입={inserted_count}, 업데이트={updated_count}, 매칭실패={not_found_count}, 오류={error_count}")

  except Exception as e:
    # 전체 예외 처리
    connection.rollback()
    logger.error(f"Error occurred: {e}")
    if hasattr(e, 'args'):
      logger.error(f"Error details: {e.args}")
    raise

  finally:
    # 마무리 작업
    cursor.close()
    connection.close()

  return {
    "inserted": inserted_count,
    "updated": updated_count,
    "not_found": not_found_count,
    "error": error_count
  }

# 직접 실행할 때만 사용
if __name__ == "__main__":
  # 로깅 설정
  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(levelname)s - %(message)s',
      handlers=[logging.StreamHandler(sys.stdout)]
  )

  # 환경 변수에서 DB 설정 가져오기
  db_config = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'port': int(os.environ.get('MYSQL_PORT', 3306)),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', '1234'),
    'database': os.environ.get('MYSQL_DB', 'skku')
  }

  csv_file_path = 'kakao_map_ranks.csv'
  insert_ranks(db_config, csv_file_path)