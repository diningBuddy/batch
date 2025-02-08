# initial-es-index.py
import json
import os
from elasticsearch import Elasticsearch, helpers, logger
import mysql.connector
import datetime
from dotenv import load_dotenv

load_dotenv()

# ES 연결 설정
ES_HOST = os.getenv('ES_HOST', 'es-singlenode')
es = Elasticsearch([f'http://{ES_HOST}:9200'])

def fetch_initial_data():
  connection = mysql.connector.connect(
      user='skku-user',
      password='skku-pw',
      host='mysql',
      database='skku',
      port=3306
  )
  cursor = connection.cursor(dictionary=True)

  query = """
       SELECT
        r.*,
        (
            SELECT JSON_ARRAYAGG(
                JSON_OBJECT(
                    'restaurant_id', restaurant_id,
                    'menu_name', name,
                    'price', price,
                    'description', description,
                    'is_representative', is_representative,
                    'image_url', image_url
                )
            )
            FROM (
                SELECT DISTINCT m.restaurant_id, m.name, m.price, m.description, m.is_representative, m.image_url
                FROM menus m
                WHERE m.restaurant_id = r.id
            ) AS distinct_menus
        ) AS menus,
        GROUP_CONCAT(DISTINCT rc.name) AS categories
        FROM restaurants r
        LEFT JOIN restaurant_categories rcm ON r.id = rcm.restaurant_id
        LEFT JOIN categories rc ON rcm.category_id = rc.id
        GROUP BY r.id;

   """

  cursor.execute(query)
  data = cursor.fetchall()
  print(data)
  cursor.close()
  connection.close()
  return data

# 현재 시간 기반 인덱스명
now = datetime.datetime.now()
index_name = f"restaurant_{now.strftime('%Y_%m_%d_%H-%M')}"

# 인덱스 생성
if not es.indices.exists(index=index_name):
  response = es.indices.create(
      index=index_name,
      settings={
        "analysis": {
          "analyzer": {
            "korean": {
              "type": "custom",
              "tokenizer": "nori_tokenizer",
              "filter": ["nori_readingform"]
            }
          }
        }
      },
      mappings={
        "properties": {
          "id": {"type": "long"},
          "name": {"type": "text", "analyzer": "korean"},
          "address": {"type": "text", "analyzer": "korean"},
          "contact_number": {"type": "keyword"},
          "facility_infos": {"type": "object"},
          "operation_infos": {"type": "object"},
          "operation_times": {
            "type": "nested",
            "properties": {
              "day_of_the_week": {"type": "keyword"},
              "operation_time_info": {"type": "object"},
            }
          },
          "original_category": {"type": "text", "analyzer": "korean"},
          "categories": {
            "type": "keyword",
            "fields": {
              "text": {
                "type": "text",
                "analyzer": "korean"
              }
            }
          },
          "location": {"type": "geo_point"},
          "kakao_rating_count": {"type": "long"},
          "kakao_rating_avg": {"type": "float"},
          "review_count": {"type": "long"},
          "rating_avg": {"type": "float"},
          "menus": {
            "type": "nested",
            "properties": {
              "menu_name": {"type": "text", "analyzer": "korean"},
              "price": {"type": "keyword"},
              "description": {"type": "text", "analyzer": "korean"},
              "is_representative": {"type": "boolean"}
            }
          }
        }
      }
  )
  print(f"Index created: {response}")
else:
  print(f"Index already exists: {index_name}")

def index_data():
  data = fetch_initial_data()
  actions = []

  for restaurant in data:
    print(restaurant)
    try:
      # menus 처리
      menus = json.loads(restaurant['menus']) if restaurant['menus'] else []
      operation_times = json.loads(restaurant['operation_times']) if restaurant['operation_times'] else None

      categories = restaurant['categories'].split(',') if restaurant['categories'] else []

      doc = {
        "_index": index_name,
        "_id": restaurant['id'],
        "_source": {
          "id": restaurant['id'],
          "name": restaurant['name'],
          "address": restaurant['address'],
          "review_count": restaurant['review_count'],
          "rating_avg": restaurant['rating_avg'],
          "contact_number": restaurant['contact_number'],
          "facility_infos": json.loads(restaurant['facility_infos']) if restaurant['facility_infos'] else None,
          "operation_infos": json.loads(restaurant['operation_infos']) if restaurant['operation_infos'] else None,
          "kakao_rating_count": restaurant['kakao_rating_count'],
          "kakao_rating_avg": restaurant['kakao_rating_avg'],
          "operation_times": [],
          "original_category": restaurant['original_categories'],
          "categories": categories,
          "location": {
            "lat": float(restaurant['latitude']) if restaurant['latitude'] else None,
            "lon": float(restaurant['longitude']) if restaurant['longitude'] else None
          } if restaurant.get('latitude') and restaurant.get('longitude') else None,
          "menus": []
        }
      }

      # menus 데이터 정제
      if menus:
        for menu in menus:
          cleaned_menu = {
            "menu_name": menu.get('menu_name', ''),
            "price": menu.get('price', '') if menu.get('price') else '',
            "description": menu.get('description', ''),
            "is_representative": bool(menu.get('is_representative', False)),
            "image_url": menu.get('image_url','')
          }
          doc["_source"]["menus"].append(cleaned_menu)

      if operation_times:
        for operation_time in operation_times:
          processing_time = {
            "day_of_the_week": operation_time.get('day_of_the_week',''),
            "operation_time_info": operation_time.get('operation_time_info','')
          }
          doc["_source"]["operation_times"].append(processing_time)

      actions.append(doc)

    except Exception as e:
      print(f"Error processing restaurant id {restaurant['id']}: {e}")
      continue

  # 에러 상세 출력을 위한 bulk 작업
  try:
    success, failed = helpers.bulk(es, actions, raise_on_error=False)
    print(f"Successfully indexed {success} documents")
    if failed:
      print(f"Failed to index {len(failed)} documents")
      for error in failed:
        print(f"Error: {error}")
  except helpers.BulkIndexError as e:
    print(f"Bulk index error: {str(e)}")
    for error in e.errors:
      print(f"Document error: {error}")

  # 앨리어스 확인 및 설정
  if es.indices.exists_alias(name="restaurant"):
    # 기존 인덱스에서 restaurant 앨리어스 제거
    current_aliases = es.indices.get_alias(name="restaurant")
    for index in current_aliases:
      es.indices.delete_alias(index=index, name="restaurant")
      print(f"Alias 'restaurant' removed from index {index}")

  # 새 인덱스에 앨리어스 추가
  es.indices.put_alias(index=index_name, name="restaurant")
  print(f"Alias 'restaurant' created for index {index_name}")


if __name__ == "__main__":
  index_data()
  print("Initial indexing complete")
