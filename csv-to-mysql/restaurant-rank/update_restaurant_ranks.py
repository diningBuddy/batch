import pymysql
import csv
import os
import logging
import sys

logger = logging.getLogger(__name__)

def update_ranks(db_config, csv_file_path):
  logger.info(f"DB 적재 시작: {csv_file_path}, 연결: {db_config['host']}")

  connection = pymysql.connect(**db_config)
  cursor = connection.cursor()

  try:
    delete_query = "DELETE FROM restaurant_ranks"
    cursor.execute(delete_query)

    if not os.path.exists(csv_file_path):
      logger.error(f"Error: File '{csv_file_path}' not found.")
      return

    # 카테고리 정보 미리 로드
    category_map = {}
    category_query = "SELECT id, name FROM categories"
    cursor.execute(category_query)
    for cat_id, cat_name in cursor.fetchall():
      category_map[cat_name.strip()] = cat_id

    logger.info(f"로드된 카테고리 수: {len(category_map)}개")

    with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
      reader = csv.DictReader(csvfile)
      total_rows = sum(1 for _ in reader)

      csvfile.seek(0)
      next(reader)

      logger.info(f"처리할 레코드: {total_rows}개")

      inserted_count = 0
      not_found_count = 0
      category_not_found_count = 0
      error_count = 0

      for row in reader:
        try:
          restaurant_name = row['name']
          latitude = float(row['lat'])
          longitude = float(row['lon'])
          rank_number = int(row['rank'])
          category_name = row['category_name']

          # 카테고리 ID 검색
          category_id = None
          if category_name in category_map:
            category_id = category_map[category_name]
          else:
            # 카테고리명 정확히 일치하지 않을 경우 부분 일치 시도
            for db_category, cat_id in category_map.items():
              if category_name in db_category or db_category in category_name:
                category_id = cat_id
                logger.info(f"카테고리 부분 일치: '{category_name}' -> '{db_category}'")
                break

          if not category_id:
            logger.warning(f"카테고리 '{category_name}' 매칭 실패")
            category_not_found_count += 1
            # 기본 카테고리 ID 사용 (예: '기타' 카테고리)
            category_id = 60  # 기타 카테고리의 ID

          find_restaurant_query = """
                        SELECT id FROM restaurants 
                        WHERE name = %s 
                        AND ABS(latitude - %s) < 0.001 
                        AND ABS(longitude - %s) < 0.001
                        LIMIT 1
                    """
          cursor.execute(find_restaurant_query, (restaurant_name, latitude, longitude))
          result = cursor.fetchone()

          if result:
            restaurant_id = result[0]

            insert_query = """
                            INSERT INTO restaurant_ranks (restaurant_id, rank_number, category_id)
                            VALUES (%s, %s, %s)
                        """
            cursor.execute(insert_query, (restaurant_id, rank_number, category_id))
            inserted_count += 1
          else:
            not_found_count += 1
            logger.warning(f"레스토랑 '{restaurant_name}' 매칭 실패")

        except Exception as e:
          error_count += 1
          logger.error(f"Error processing row {row}: {e}")

      connection.commit()
      logger.info(f"DB 적재 결과: 삽입={inserted_count}, 매칭 실패={not_found_count}, 카테고리 매칭 실패={category_not_found_count}, 오류={error_count}")

  except Exception as e:
    connection.rollback()
    logger.error(f"Error occurred: {e}", exc_info=True)
    raise

  finally:
    cursor.close()
    connection.close()

  return {
    "inserted": inserted_count,
    "not_found": not_found_count,
    "category_not_found": category_not_found_count,
    "error": error_count
  }

if __name__ == "__main__":
  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(levelname)s - %(message)s',
      handlers=[logging.StreamHandler(sys.stdout)]
  )

  db_config = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'port': int(os.environ.get('MYSQL_PORT', 3306)),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', '1234'),
    'database': os.environ.get('MYSQL_DB', 'skku')
  }

  # 스크립트 실행 디렉토리를 기준으로 파일 경로 설정
  script_dir = os.path.dirname(os.path.abspath(__file__))
  csv_file_path = os.path.join(script_dir, 'kakao_map_ranks.csv')
  update_ranks(db_config, csv_file_path)