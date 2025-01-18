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

          # Find or insert group in categories table
          cursor.execute("SELECT id FROM categories WHERE name = %s AND parent_id IS NULL", (current_group,))
          result = cursor.fetchone()

          if result:
            group_id = result[0]
          else:
            cursor.execute("INSERT INTO categories (name, parent_id) VALUES (%s, NULL)", (current_group,))
            group_id = cursor.lastrowid

        elif group_id is not None:  # 소분류 처리
          category_name = line
          print(f"Adding category: {category_name} under group_id: {group_id}")  # 디버깅 로그

          cursor.execute("SELECT COUNT(*) FROM categories WHERE name = %s AND parent_id = %s", (category_name, group_id))
          (count,) = cursor.fetchone()

          if count == 0:  # 중복이 없을 때만 삽입
            cursor.execute("INSERT INTO categories (name, parent_id) VALUES (%s, %s)", (category_name, group_id))

    # 모든 작업 후 커밋
    connection.commit()
    print("Categories successfully inserted.")

  except Exception as e:
    print(f"Error: {e}")
    connection.rollback()
  finally:
    cursor.close()
    connection.close()
