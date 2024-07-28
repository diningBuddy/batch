import datetime

import pandas as pd
from elasticsearch import Elasticsearch

restaurant_df = pd.read_csv('../autocomplete/restaurants.csv')
menu_df = pd.read_csv('../autocomplete/menus.csv')

now = datetime.datetime.now()
index_name = f"restaurant_{now.strftime('%Y_%m_%d_%H-%M')}"

# Elasticsearch 클라이언트 설정
es = Elasticsearch("http://localhost:9200")

# 새 인덱스 생성 및 매핑 설정
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body={
        "settings": {
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
        "mappings": {
            "properties": {
                "id": {"type": "long"},
                "name": {"type": "text", "analyzer": "korean"},
                "original_category": {"type": "text", "analyzer": "korean"},
                "address": {"type": "text", "analyzer": "korean"},
                "naver_review_count": {"type": "long"},
                "naver_rating_avg": {"type": "float"},
                "review_count": {"type": "long"},
                "rating_avg": {"type": "float"},
                "like_count": {"type": "long"},
                "number": {"type": "text"},
                "image_url": {"type": "text"},
                "category": {"type": "text", "analyzer": "korean"},
                "discount_content": {"type": "text", "analyzer": "korean"},
                "location": {"type": "geo_point"},
                "menus": {
                    "type": "nested",
                    "properties": {
                        "menu_name": {"type": "text", "analyzer": "korean"},
                        "price": {"type": "integer"},
                        "description": {"type": "text", "analyzer": "korean"},
                        "is_representative": {"type": "text"},
                        "image_url": {"type": "text"}
                    }
                }
            }
        }
    })

# 데이터 인덱싱
for _, row in restaurant_df.iterrows():
    menus = menu_df[menu_df['restaurant_id'] == row['id']].to_dict('records')

    for menu in menus:
        if pd.isna(menu['image_url']):
            menu.pop('image_url')  # image_url 필드가 NaN이면 제거

        menu['price'] = int(menu['price'].replace(',', ''))  # 가격에서 쉼표 제거 및 정수 변환
        menu['is_representative'] = menu['is_representative'] == '대표'  # 대표 여부를 Boolean 값으로 변환

    if pd.isna(row['image_url']):
        restaurant_image_url = None  # NaN 값을 None으로 설정
    else:
        restaurant_image_url = row['image_url']

    if pd.notna(row['rating']):
        rating = float(row['rating'])
    else:
        rating = None

    if pd.notna(row['number']):
        number = row['number']
    else:
        number = None

    if pd.notna(row['discount_content']):
        discount_content = row['discount_content']
    else:
        discount_content = None

    if pd.notna(row['longitude']) and pd.notna(row['latitude']):
        location = {"lat": float(row['latitude']), "lon": float(row['longitude'])}
    else:
        location = None

    print(row['name'], row['category'], row['review_count'], row['address'], rating, number, restaurant_image_url,
          menus, location)
    data = {
        "id": row['id'],
        "name": row['name'],
        "original_category": row['category'],
        "naver_review_count": row['review_count'].replace('+', ''),
        "address": row['address'],
        "naver_rating_avg": rating,
        "number": number,
        "image_url": restaurant_image_url,
        "category": row['custom_category'],
        "discount_content": discount_content,
        "location": location,
        "menus": menus,
    }
    if data.get("discount_content") is None:
        data.pop("discount_content")
    if data.get("naver_review_count") is None:
        data.pop("naver_review_count")
    if data.get("naver_rating_avg") is None:
        data.pop("naver_rating_avg")
    if data.get("number") is None:
        data.pop("number")
    if data.get("image_url") is None:
        data.pop("image_url")
    if data.get("location") is None:
        data.pop("location")

    response = es.index(index=index_name, id=row['id'], document=data)
    print(f"Indexed document ID: {response['_id']}, Result: {response['result']}")

# 앨리어스 확인 및 설정
if not es.indices.exists_alias(name="restaurant"):
    # 앨리어스가 없으면 새 인덱스에 앨리어스 생성
    es.indices.put_alias(index=index_name, name="restaurant")
else:
    # 기존에 앨리어스가 있다면, 앨리어스를 새 인덱스로 업데이트하고, 기존 인덱스 삭제
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

print("Indexing complete, and alias updated.")
