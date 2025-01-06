# insert_menus.py
import csv
import pymysql
import codecs

def insert_menus(db_config, csv_file_path):
  connection = pymysql.connect(**db_config)
  cursor = connection.cursor()

  try:
    with codecs.open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        # 디버깅을 위해 각 행을 출력
        print(f"Processing row: {row}")

        # Ensure restaurant_id is present and convert to int
        restaurant_id_str = row.get('restaurant_id', '').strip()
        if not restaurant_id_str.isdigit():
          print(f"Skipping menu entry due to invalid or missing restaurant_id: {restaurant_id_str}")
          continue

        restaurant_id = int(restaurant_id_str)

        # Check if restaurant exists by its 'id'
        cursor.execute("SELECT COUNT(*) FROM restaurants WHERE id = %s", (restaurant_id,))
        (count,) = cursor.fetchone()

        if count == 0:
          print(f"Skipping menu entry, restaurant_id {restaurant_id} not found in restaurants table.")
          continue

        # Convert empty strings to None for certain fields
        price = int(row['price'].strip().replace(',','')) if row['price'] else None
        description = row['description'].strip() if row['description'] else None
        is_representative = True if row['is_representative'].strip() == '대표' else False
        image_url = row['image_url'].strip() if row['image_url'] else None

        # Check if menu already exists by restaurant_id and menu_name
        cursor.execute("SELECT COUNT(*) FROM menus WHERE restaurant_id = %s AND name = %s", (restaurant_id, row['menu_name']))
        (count,) = cursor.fetchone()

        if count > 0:
          # If menu exists, update the existing entry
          update_query = (
            "UPDATE menus SET price=%s, description=%s, is_representative=%s, image_url=%s "
            "WHERE restaurant_id=%s AND name=%s"
          )
          cursor.execute(update_query, (
            price, description, is_representative, image_url, restaurant_id, row['menu_name']
          ))
        else:
          # Insert a new menu entry
          insert_query = (
            "INSERT INTO menus (restaurant_id, name, price, description, is_representative, image_url) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
          )
          cursor.execute(insert_query, (
            restaurant_id, row['menu_name'], price, description, is_representative, image_url
          ))

        # Commit after each row to ensure data integrity
        connection.commit()
  except Exception as e:
    print(f"Error: {e}")
    connection.rollback()
  finally:
    cursor.close()
    connection.close()
