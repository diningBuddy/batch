import json
import os
import openai
import pymysql
import redis

# MySQL 연결 설정
conn = pymysql.connect(
  host="skku-db",
  port=3306,
  user="skku-user",
  password="skku-pw",
  db="skku",
  charset='utf8'
)

# Redis 연결 설정
redis_client = redis.StrictRedis(host='skku-redis', port=6379, db=0,
                                 decode_responses=True)

SEARCH_PREFIX = "SR:"
MAX_HISTORY = 5

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_search_queries(user_id):
  key = f"{SEARCH_PREFIX}{user_id}"
  return redis_client.lrange(key, 0, MAX_HISTORY - 1)


def get_filtered_restaurants():
  query_restaurants = """
    SELECT id, name, original_categories, naver_rating_avg, naver_review_count
    FROM restaurants
    WHERE naver_rating_avg >= 4.5 AND naver_review_count >= 200;
    """
  with conn.cursor() as cursor:
    cursor.execute(query_restaurants)
    return cursor.fetchall()


def get_user_liked_restaurants():
  query_liked_restaurants = """
    SELECT u.id AS user_id, r.name AS restaurant_name, r.original_categories AS category
    FROM users u
    JOIN restaurant_likes rl ON u.id = rl.user_id
    JOIN restaurants r ON rl.restaurant_id = r.id;
    """
  with conn.cursor() as cursor:
    cursor.execute(query_liked_restaurants)
    return cursor.fetchall()


def get_gpt_recommendations(user_data, restaurant_data):
  prompt = f"""
    유저가 데이터랑, 음식점 데이터를 보여줄게.
    이걸 기반으로 음식점을 20개 추천해줘.
    다른 이야기는 다 빼고 추천할 음식점id를 ","기반으로 구분해서 리스트로 알려줘

    User Data:
    {json.dumps(user_data)}

    Restaurant Data:
    {json.dumps(restaurant_data)}
    """
  response = openai.ChatCompletion.create(
    model="gpt-4-turbo",
    messages=[
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": prompt}
    ],
    max_tokens=2000
  )
  return response['choices'][0]['message']['content'].strip()


def save_recommendations_to_redis(user_id, recommendations):
  key = f"RECOMMENDATION:{user_id}"
  redis_client.delete(key)
  redis_client.set(key, recommendations)
  redis_client.expire(key, 3600 * 24 * 3)


def save_all_restaurants_to_redis(filtered_restaurants):
  all_restaurant_ids = [str(restaurant[0]) for restaurant in
                        filtered_restaurants]
  recommendations_string = ','.join(all_restaurant_ids)
  save_recommendations_to_redis(0, recommendations_string)


filtered_restaurants = get_filtered_restaurants()
user_liked_restaurants = get_user_liked_restaurants()

user_data = {}
for liked_restaurant in user_liked_restaurants:
  user_id = liked_restaurant[0]
  restaurant_name = liked_restaurant[1]
  category = liked_restaurant[2]

  if user_id not in user_data:
    user_data[user_id] = {'liked_restaurants': [], 'recent_searches': []}

  user_data[user_id]['liked_restaurants'].append({
    'restaurant_name': restaurant_name,
    'category': category
  })

for user_id in user_data.keys():
  recent_searches = get_search_queries(user_id)
  user_data[user_id]['recent_searches'] = recent_searches

restaurant_data = [dict(zip(
  ['id', 'name', 'original_categories', 'naver_rating_avg',
   'naver_review_count'], restaurant)) for restaurant in filtered_restaurants]

print("restaurant_data", restaurant_data, "length:", len(restaurant_data))
for user_id, data in user_data.items():
  print("user_id", user_id, "data", data)
  try:
    recommendations = get_gpt_recommendations(data, restaurant_data)
  except:
    continue
  print(recommendations)
  save_recommendations_to_redis(user_id, recommendations)

save_all_restaurants_to_redis(filtered_restaurants)
