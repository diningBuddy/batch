import csv

import pymysql

from create_table import create_table
from insert import *

# connect to MySQL server
conn = pymysql.connect(
  host="127.0.0.1",
  port=3306,
  user="skku-user",
  password="skku-pw",
  db="skku",
  charset='utf8'
)

# table creation query(restaurants, restaurant_likes)
cursor = conn.cursor()
create_table(cursor)
conn.commit()

# Insert restaurants, categories
with open('../csv/restaurants.csv', mode='r') as file:
  csv_dict = csv.DictReader(file)
  categories = dict()
  category_id = 1
  restaurants = []
  for restaurant in csv_dict:
    restaurants.append(restaurant)
    if restaurant['custom_category'] not in categories:
      categories[restaurant['custom_category']] = category_id
      category_id += 1

  for c in categories:
    insert_into_categories(cursor, categories[c], c)

  for restaurant in restaurants:
    insert_into_restaurants(cursor, restaurant)
    insert_into_restaurant_categories(
      cursor,
      restaurant['id'],
      categories[restaurant['custom_category']]
    )

conn.commit()

# Insert menus
with open('../csv/menus.csv', mode='r') as file:
  csv_dict = csv.DictReader(file)
  for menu in csv_dict:
    insert_into_menus(cursor, menu)

conn.commit()

# close the connection
conn.close()
