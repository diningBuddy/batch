# insert_category_mapping.py
import pymysql

def insert_category_mapping(db_config):
  connection = pymysql.connect(**db_config)
  cursor = connection.cursor()

  try:
    # Get all restaurants and their original categories
    cursor.execute("SELECT id, original_categories FROM restaurants")
    restaurants = cursor.fetchall()

    for restaurant_id, original_category in restaurants:
      if not original_category:
        continue

      # Find the matching category id in restaurant_categories (소분류 우선 검색)
      cursor.execute("SELECT id FROM restaurant_categories WHERE name = %s", (original_category,))
      result = cursor.fetchone()

      if result:
        category_id = result[0]
      else:
        # 매칭되는 소분류가 없으면 스킵
        continue

      # Check if mapping already exists
      cursor.execute(
          "SELECT COUNT(*) FROM restaurant_categories_mapping WHERE restaurant_id = %s AND category_id = %s",
          (restaurant_id, category_id)
      )
      (count,) = cursor.fetchone()

      if count == 0:
        # Insert the mapping if it doesn't exist
        cursor.execute(
            "INSERT INTO restaurant_categories_mapping (restaurant_id, category_id) VALUES (%s, %s)",
            (restaurant_id, category_id)
        )
        connection.commit()

  except Exception as e:
    print(f"Error: {e}")
    connection.rollback()
  finally:
    cursor.close()
    connection.close()
