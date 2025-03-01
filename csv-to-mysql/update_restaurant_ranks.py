import pymysql
import csv
import os

def insert_ranks(db_config, csv_file_path):
  connection = pymysql.connect(**db_config)
  cursor = connection.cursor()

  try:
    # 파일 존재 확인
    if not os.path.exists(csv_file_path):
      print(f"Error: File '{csv_file_path}' not found.")
      return

    # CSV 파일 읽기
    with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
      reader = csv.DictReader(csvfile)

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

            # VALUES() 함수를 사용하지 않는 대체 방법
            # 1. 먼저 존재 여부 확인
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
            else:
              # 없으면 INSERT
              insert_query = """
                            INSERT INTO restaurant_ranks (restaurant_id, rank_number)
                            VALUES (%s, %s)
                            """
              cursor.execute(insert_query, (restaurant_id, rank_number))

        except Exception as e:
          print(f"Error processing row {row}: {e}")
          # 개별 오류가 전체 처리를 중단하지 않도록 예외 처리

      # 모든 처리가 끝난 후 커밋
      connection.commit()
      print(f"Successfully inserted rank data from {csv_file_path}")

  except Exception as e:
    # 전체 예외 처리
    connection.rollback()
    print(f"Error occurred: {e}")
    print(f"Error type: {type(e)}")
    if hasattr(e, 'args'):
      print(f"Error details: {e.args}")

  finally:
    # 마무리 작업
    cursor.close()
    connection.close()

if __name__ == "__main__":
  db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '1234',
    'database': 'skku'
  }

  csv_file_path = 'kakao_map_ranks.csv'
  insert_ranks(db_config, csv_file_path)