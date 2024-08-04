def insert_into_restaurants(cursor, restaurant):
  insert_query = """
    INSERT INTO `restaurants` (
      `id`,
      `name`, 
      `original_categories`, 
      `review_count`, 
      `like_count`, 
      `address`, 
      `contact_number`, 
      `rating_avg`, 
      `representative_image_url`, 
      `view_count`,
      `discount_content`,
      `longitude`,
      `latitude`,
      `naver_rating_avg`,
      `naver_review_count`
    ) 
    VALUES (
      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    );
    """
  cursor.execute(insert_query, (
    restaurant['id'],
    restaurant['name'],
    restaurant['category'],
    0,
    0,
    restaurant['address'],
    restaurant['number'],
    0,
    restaurant['image_url'],
    0,
    restaurant['discount_content'],
    restaurant['longitude'],
    restaurant['latitude'],
    0.0 if restaurant['rating'] == '' else float(restaurant['rating']),
    int(restaurant['review_count'].replace('+', ''))
  ))


def insert_into_categories(cursor, id, name):
  insert_query = """
        INSERT IGNORE INTO categories (id, name)
        VALUES (%s, %s);
        """

  cursor.execute(insert_query, (
    id,
    name
  ))


def insert_into_restaurant_categories(cursor, restaurant_id, category_id):
  insert_query = """
          INSERT IGNORE INTO restaurant_categories (restaurant_id, category_id)
          VALUES (%s, %s);
          """

  cursor.execute(insert_query, (
    restaurant_id,
    category_id
  ))


def insert_into_operating_infos(cursor, operation):
  insert_query = """
        INSERT IGNORE INTO operating_infos (restaurant_id, day, info)
        VALUES (%s, %s, %s);
        """

  cursor.execute(insert_query, (
    operation['restaurant_id'],
    operation['day'],
    operation['info']
  ))


def insert_into_menus(cursor, menu):
  insert_query = """
        INSERT IGNORE INTO menus (
          restaurant_id, 
          name,
          price,
          description,
          is_representative,
          image_url
        )
        VALUES (%s, %s, %s, %s, %s, %s);
        """

  cursor.execute(insert_query, (
    menu['restaurant_id'],
    menu['menu_name'],
    int(menu['price'].replace(',', '')),
    menu['description'] if menu['description'] != "설명 없음" else "",
    1 if menu['is_representative'] == '대표' else 0,
    menu['image_url']
  ))
