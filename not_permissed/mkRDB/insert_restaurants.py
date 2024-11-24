# insert_restaurants.py
import csv
import pymysql
import json

def insert_restaurants(db_config, csv_file_path):
  connection = pymysql.connect(**db_config)
  cursor = connection.cursor()

  try:
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        # Convert empty strings to None for DECIMAL fields
        kakao_rating_avg = float(row['rating']) if row['rating'] else None
        kakao_rating_count = int(float(row['rating_count'])) if row['rating_count'] else None
        latitude = float(row['latitude']) if row['latitude'] else None
        longitude = float(row['longitude']) if row['longitude'] else None

        # Check if restaurant already exists by its 'id'
        cursor.execute("SELECT COUNT(*) FROM restaurants WHERE id = %s", (row['id'],))
        (count,) = cursor.fetchone()

        # Prepare JSON fields
        facility_infos = json.dumps({
          "wifi": row['wifi'],
          "pet": row['pet'],
          "parking": row['parking'],
          "nursery": row['nursery'],
          "smokingroom": row['smokingroom'],
          "fordisabled": row['fordisabled']
        })

        operation_infos = json.dumps({
          "appointment": row['appointment'],
          "delivery": row['delivery'],
          "package": row['package']
        })

        operation_times = row['operation_time']  # Assuming operation_time is already in JSON format

        if count > 0:
          # If restaurant exists, update the existing entry
          update_query = (
            "UPDATE restaurants SET name=%s, original_category=%s, review_count=%s, address=%s, "
            "contact_number=%s, kakao_rating_avg=%s, kakao_rating_count=%s, facility_infos=%s, operation_infos=%s, operation_times=%s, latitude=%s, longitude=%s "
            "WHERE id=%s"
          )
          cursor.execute(update_query, (
            row['name'], row['category'], row['review_count'], row['address'],
            row['phone_number'], kakao_rating_avg, kakao_rating_count,
            facility_infos, operation_infos, operation_times, latitude, longitude, row['id']
          ))
        else:
          # Insert a new restaurant entry
          insert_query = (
            "INSERT INTO restaurants (id, name, original_category, review_count, address, contact_number, "
            "kakao_rating_avg, kakao_rating_count, facility_infos, operation_infos, operation_times, latitude, longitude) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
          )
          cursor.execute(insert_query, (
            row['id'], row['name'], row['category'], row['review_count'], row['address'],
            row['phone_number'], kakao_rating_avg, kakao_rating_count,
            facility_infos, operation_infos, operation_times, latitude, longitude
          ))

        # Commit after each row to ensure data integrity
        connection.commit()
  except Exception as e:
    print(f"Error: {e}")
    connection.rollback()
  finally:
    cursor.close()
    connection.close()