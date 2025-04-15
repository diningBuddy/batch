import pymysql
import csv
import os
import logging
import sys
import glob

logger = logging.getLogger(__name__)

def update_ranks(db_config, csv_directory):
  """여러 카테고리 CSV 파일을 처리하여 DB에 적재하는 함수"""
  logger.info(f"DB 적재 시작: 디렉토리 {csv_directory}, 연결: {db_config['host']}")

  connection = pymysql.connect(**db_config)
  cursor = connection.cursor()

  try:
    delete_query = "DELETE FROM popular_restaurants"
    cursor.execute(delete_query)
    logger.info("기존 데이터 삭제 완료")

    csv_files = glob.glob(os.path.join(csv_directory, "kakao_map_ranks_category_*.csv"))

    if not csv_files:
      logger.warning(f"카테고리 CSV 파일을 찾을 수 없습니다: {csv_directory}")
      return

    total_inserted = 0
    total_not_found = 0
    total_error = 0

    for csv_file_path in csv_files:
      file_name = os.path.basename(csv_file_path)
      category = file_name.replace("kakao_map_ranks_", "").replace(".csv", "")

      display_category = category.replace("category_", "").upper()

      logger.info(f"처리 중인 파일: {file_name}, 카테고리: {display_category}")

      if not os.path.exists(csv_file_path):
        logger.error(f"Error: File '{csv_file_path}' not found.")
        continue

      with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        total_rows = sum(1 for _ in reader)

        csvfile.seek(0)
        next(reader)

        logger.info(f"처리할 레코드: {total_rows}개")

        inserted_count = 0
        not_found_count = 0
        error_count = 0

        for row in reader:
          try:
            restaurant_name = row['name']
            latitude = float(row['lat'])
            longitude = float(row['lon'])
            rank_number = int(row['rank'])

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
                                INSERT INTO popular_restaurants (restaurant_id, rank_number, scrap_category)
                                VALUES (%s, %s, %s)
                            """
              cursor.execute(insert_query, (restaurant_id, rank_number, display_category))
              inserted_count += 1
            else:
              not_found_count += 1
              logger.warning(f"레스토랑 '{restaurant_name}' 매칭 실패")

          except Exception as e:
            error_count += 1
            logger.error(f"Error processing row {row}: {e}")

        logger.info(f"카테고리 {display_category} 처리 완료: 성공 {inserted_count}, 매칭실패 {not_found_count}, 오류 {error_count}")

        total_inserted += inserted_count
        total_not_found += not_found_count
        total_error += error_count

    connection.commit()
    logger.info(f"전체 처리 결과: 성공 {total_inserted}, 매칭실패 {total_not_found}, 오류 {total_error}")

  except Exception as e:
    connection.rollback()
    logger.error(f"Error occurred: {e}", exc_info=True)
    raise

  finally:
    cursor.close()
    connection.close()

  return {
    "inserted": total_inserted,
    "not_found": total_not_found,
    "error": total_error
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

  script_dir = os.path.dirname(os.path.abspath(__file__))
  update_ranks(db_config, script_dir)
