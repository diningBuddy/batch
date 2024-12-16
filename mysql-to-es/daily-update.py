# daily-update.py
import os
from elasticsearch import Elasticsearch, helpers
import mysql.connector
from dotenv import load_dotenv
import re

load_dotenv()

ES_HOST = os.getenv('ES_HOST', 'es-singlenode')#ES_HOST docker-compose에 있는,es-singlenode는 docker에서es의 이름
es = Elasticsearch([f'http://{ES_HOST}:9200'])

# Alias 이름
ALIAS_NAME = "restaurant_latest"


def fetch_user_activity_data():
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
    r.id AS id,
    COALESCE(r.bookmark_count,0) AS bookmark_count,
    COALESCE(r.kakao_rating_avg, 0) AS rating_avg,
    COALESCE(r.kakao_rating_count,0) AS rating_count
    FROM restaurants r
    LEFT JOIN restaurant_bookmarks rb ON r.id = rb.restaurant_id
    LEFT JOIN restaurants_ratings rr ON r.id = rr.restaurant_id
    GROUP BY r.id;
    """

  cursor.execute(query)
  data = cursor.fetchall()
  cursor.close()
  connection.close()
  return data

def update_elasticsearch(data):

  # 최신 인덱스 찾기
  sorted_indices = get_sorted_indices()
  latest_index = sorted_indices[-1]

  actions = [
    {
      "_op_type": "update",
      "_index": latest_index,
      "_id": restaurant['id'],
      "doc": {
        "bookmark_count": restaurant['bookmark_count'],
        "rating_avg": float(restaurant['rating_avg']) if restaurant['rating_avg'] else None,
        "rating_count": restaurant['rating_count']
      },
      "doc_as_upsert": True
    }
    for restaurant in data
    if restaurant['id'] is not None
  ]

  helpers.bulk(es, actions)

def get_sorted_indices():
  """Elasticsearch의 인덱스를 날짜 기준으로 정렬"""
  indices = es.indices.get_alias(index="*")
  pattern = r"restaurant_\d{4}_\d{2}_\d{2}_\d{2}-\d{2}"  # 예: restaurant_2024_11_24_02-00
  sorted_indices = sorted(
      [index for index in indices if re.match(pattern, index)],
      key=lambda x: x.split("_")[1:],  # 날짜를 기준으로 정렬
  )
  return sorted_indices

def update_alias(latest_index):
  """Alias를 최신 인덱스로 업데이트"""
  try:
    es.indices.update_aliases({
      "actions": [
        {"remove": {"index": "*", "alias": ALIAS_NAME}},  # 기존 Alias 제거
        {"add": {"index": latest_index, "alias": ALIAS_NAME}},  # 새로운 Alias 추가
      ]
    })
    print(f"Alias '{ALIAS_NAME}'가 '{latest_index}'로 업데이트되었습니다.")
  except Exception as e:
    print(f"Alias 업데이트 실패: {e}")

def delete_oldest_index(sorted_indices):
  """가장 오래된 인덱스 삭제"""
  if len(sorted_indices) > 1:  # 최소 2개 이상의 인덱스가 있어야 삭제 진행
    oldest_index = sorted_indices[0]
    try:
      es.indices.delete(index=oldest_index)
      print(f"가장 오래된 인덱스 '{oldest_index}'가 삭제되었습니다.")
    except Exception as e:
      print(f"인덱스 삭제 실패: {e}")
  else:
    print("삭제할 인덱스가 충분하지 않습니다.")

if __name__ == "__main__":
  user_activity_data = fetch_user_activity_data()
  update_elasticsearch(user_activity_data)

  try:
    sorted_indices = get_sorted_indices()
    latest_index = sorted_indices[-1]
    update_alias(latest_index)
    delete_oldest_index(sorted_indices)

    print("Daily update complete")
  except Exception as e:
    print(f"Update failed: {e}")
