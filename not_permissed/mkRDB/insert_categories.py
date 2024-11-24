# insert_categories.py
import pymysql
import codecs

def insert_categories(db_config, txt_file_path):
  connection = pymysql.connect(**db_config)
  cursor = connection.cursor()

  try:
    with codecs.open(txt_file_path, 'r', encoding='utf-8-sig') as txtfile:
      current_group = None
      group_id = None
      for line in txtfile:
        line = line.strip()
        if not line:
          continue

        # 대분류 식별: 숫자와 점(.)으로 시작하는 줄
        if line[0].isdigit() and '.' in line:
          # 대분류 이름 추출
          current_group = line.split('.', 1)[1].strip()
          print(f"Processing group: {current_group}")  # 디버깅 로그

          # Find or insert group in restaurant_categories table
          cursor.execute("SELECT id FROM restaurant_categories WHERE name = %s AND category_groups = %s", (current_group, current_group))
          result = cursor.fetchone()

          if result:
            group_id = result[0]
          else:
            cursor.execute("INSERT INTO restaurant_categories (name, category_groups) VALUES (%s, %s)", (current_group, current_group))
            connection.commit()
            group_id = cursor.lastrowid
        elif group_id is not None:  # 소분류 식별 (대분류가 설정된 경우에만 처리)
          category_name = line
          print(f"Adding category: {category_name} under group_id: {group_id}")  # 디버깅 로그

          cursor.execute("SELECT COUNT(*) FROM restaurant_categories WHERE name = %s AND category_groups = %s", (category_name, current_group))
          (count,) = cursor.fetchone()

          if count > 0:
            # 이미 존재하므로 업데이트 필요 없음
            continue
          else:
            cursor.execute("INSERT INTO restaurant_categories (name, category_groups) VALUES (%s, %s)", (category_name, current_group))
            connection.commit()

  except Exception as e:
    print(f"Error: {e}")
    connection.rollback()
  finally:
    cursor.close()
    connection.close()