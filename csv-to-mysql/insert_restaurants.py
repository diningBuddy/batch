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
        cursor.execute("SELECT COUNT(*) FROM restaurants WHERE name = %s", (row['name'],))
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

        operation_times = json.loads(row['operation_time'].replace('""','"'))

        operation_times_list = []

        # 각 요일을 순회하여 구조 변환
        for day, times in list(operation_times.items()):
          operation_time_info = {
            "start_time": times["시작시간"],
            "end_time": times["종료시간"],
            "break_start_time": times["휴게시작시간"],
            "break_end_time": times["휴게종료시간"],
            "last_order": times["라스트오더"]
          }
          operation_times_list.append({
            "day_of_the_week": day,
            "operation_time_info": operation_time_info
          })

        operation_times_json = json.dumps(operation_times_list)
        bookmark_count =0;
        view_count =0;

        if count > 0:
          update_query = (
            "UPDATE restaurants "
            "SET "
            "name=%s, "
            "original_categories=%s, "
            "review_count=%s, "
            "address=%s, "
            "contact_number=%s, "
            "kakao_rating_avg=%s, "
            "kakao_rating_count=%s, "
            "facility_infos=%s, "
            "operation_infos=%s, "
            "operation_times=%s, "
            "latitude=%s, "
            "longitude=%s, "
            "representative_image_url=%s"
            "WHERE id=%s"
          )
          cursor.execute(update_query,
                         (
                                row['name'],
                                row['category'],
                                row['review_count'],
                                row['address'],
                                row['phone_number'],
                                kakao_rating_avg,
                                kakao_rating_count,
                                facility_infos,
                                operation_infos,
                                operation_times_json,
                                latitude,
                                longitude,
                                row['main_photo_url'],
                                row['id']
                              )
                         )
        else:
          # Insert a new restaurant entry
          insert_query = (
                          "INSERT INTO restaurants ("
                                                    "id, "
                                                    "name, "
                                                    "original_categories, "
                                                    "review_count, "
                                                    "address, "
                                                    "contact_number, "
                                                    "kakao_rating_avg, "
                                                    "kakao_rating_count, "
                                                    "facility_infos, "
                                                    "operation_infos, "
                                                    "operation_times, "
                                                    "latitude, "
                                                    "longitude,"
                                                    "bookmark_count,"
                                                    "view_count, "
                                                    "representative_image_url"
                                                    ")"
                          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        )
          cursor.execute(insert_query,
                         (
                                row['id'],
                                row['name'],
                                row['category'],
                                row['review_count'],
                                row['address'],
                                row['phone_number'],
                                kakao_rating_avg,
                                kakao_rating_count,
                                facility_infos,
                                operation_infos,
                                operation_times_json,
                                latitude,
                                longitude,
                                bookmark_count,
                                view_count,
                                row['main_photo_url']
                              )
                         )

        connection.commit()
  except Exception as e:
    print(f"Error: {e}")
    connection.rollback()
  finally:
    cursor.close()
    connection.close()
