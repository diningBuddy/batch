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
                    'menu_name', menu_name,
                    'price', price,
                    'description', description,
                    'is_representative', is_representative,
                    'image_url', image_url
                )
            )
            FROM (
                SELECT DISTINCT m.menu_name, m.price, m.description, m.is_representative, m.image_url
                FROM menus m
                WHERE m.restaurant_id = r.id
            ) AS distinct_menus
        ) AS menus,
        GROUP_CONCAT(DISTINCT rc.name) AS categories
        FROM restaurants r
        LEFT JOIN restaurant_category_mapping rcm ON r.id = rcm.restaurant_id
        LEFT JOIN restaurant_categories rc ON rcm.category_id = rc.id
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
  es.indices.create(
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
          "operation_times": {"type": "object"},
          "original_category": {"type": "text", "analyzer": "korean"},
          "categories": {"type": "keyword"},  # 변경
          "location": {"type": "geo_point"},
          "menus": {
            "type": "nested",
            "properties": {
              "menu_name": {"type": "text", "analyzer": "korean"},
              "price": {"type": "keyword"},  # 변경
              "description": {"type": "text", "analyzer": "korean"},
              "is_representative": {"type": "boolean"}
            }
          }
        }
      }
  )

def index_data():
  data = fetch_initial_data()
  actions = []
  for restaurant in data:
    print(restaurant)
    try:
      # menus 처리
      menus = json.loads(restaurant['menus']) if restaurant['menus'] else []

      # categories 처리
      categories = restaurant['categories'].split(',') if restaurant['categories'] else []

      doc = {
        "_index": index_name,
        "_id": restaurant['id'],
        "_source": {
          "id": restaurant['id'],
          "name": restaurant['name'],
          "address": restaurant['address'],
          "contact_number": restaurant['contact_number'],
          "facility_infos": json.loads(restaurant['facility_infos']) if restaurant['facility_infos'] else None,
          "operation_infos": json.loads(restaurant['operation_infos']) if restaurant['operation_infos'] else None,
          "operation_times": json.loads(restaurant['operation_times']) if restaurant['operation_times'] else None,
          "original_category": restaurant['original_category'],
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
            "price": menu.get('price', '').replace(',', '') if menu.get('price') else '',
            "description": menu.get('description', ''),
            "is_representative": bool(menu.get('is_representative', False))
          }
          doc["_source"]["menus"].append(cleaned_menu)

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

  # Update alias
  if not es.indices.exists_alias(name="restaurant"):
    es.indices.put_alias(index=index_name, name="restaurant")
  else:
    old_indices = list(es.indices.get_alias(name="restaurant").keys())
    es.indices.update_aliases(body={
      "actions": [
        {"remove": {"index": "*", "alias": "restaurant"}},
        {"add": {"index": index_name, "alias": "restaurant"}}
      ]
    })
    for idx in old_indices:
      if idx != index_name:
        es.indices.delete(index=idx)

if __name__ == "__main__":
  index_data()
  print("Initial indexing complete")
