import mysql.connector
from elasticsearch import Elasticsearch, helpers

db_config = {
  'user': 'skku-user',
  'password': 'skku-pw',
  'host': 'skku-db',
  'database': 'skku',
  'port': 3306
}

es = Elasticsearch(['http://es-singlenode:9200'])


def fetch_restaurant_data():
  connection = mysql.connector.connect(**db_config)
  cursor = connection.cursor(dictionary=True)

  query = """
    SELECT id, name, rating_avg, review_count, like_count 
    FROM restaurants
    """

  cursor.execute(query)
  data = cursor.fetchall()

  cursor.close()
  connection.close()

  return data


def update_elasticsearch(data):
  actions = [
    {
      "_op_type": "update",
      "_index": "restaurant",
      "_id": restaurant['id'],
      "doc": {
        "rating_avg": restaurant['rating_avg'],
        "review_count": restaurant['review_count'],
        "like_count": restaurant['like_count']
      },
      "doc_as_upsert": True
    }
    for restaurant in data
  ]

  helpers.bulk(es, actions)


restaurant_data = fetch_restaurant_data()
update_elasticsearch(restaurant_data)
print("Elasticsearch update complete")
