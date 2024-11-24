# create_table_manager.py
import pymysql

def create_database_tables(db_config):
  connection = pymysql.connect(**db_config)
  cursor = connection.cursor()

  try:
    # Create restaurants table
    create_restaurants_table(cursor)
    # Create menus table
    create_menus_table(cursor)
    # Create restaurant_categories table
    create_restaurant_categories_table(cursor)
    # Create restaurant_category_mapping table
    create_restaurant_category_mapping_table(cursor)
    # Create restaurants_ratings table
    create_restaurants_ratings_table(cursor)
    create_restaurant_bookmark_lists(cursor)
    create_restaurant_bookmark_list_mapping(cursor)
    # Create restaurant_bookmarks table
    create_restaurant_bookmarks_table(cursor)

    connection.commit()
    print("Tables created successfully (if not exists).")
  except Exception as e:
    print(f"Error creating tables: {e}")
    connection.rollback()
  finally:
    cursor.close()
    connection.close()

def create_restaurants_table(cursor):
  create_table_query = (
    """
    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER NOT NULL AUTO_INCREMENT,
        name VARCHAR(100) NOT NULL COMMENT '식당 이름',
        original_category VARCHAR(255) DEFAULT NULL COMMENT '카테고리 (크롤링된)',
        review_count INTEGER DEFAULT NULL COMMENT '리뷰 개수',
        address VARCHAR(255) DEFAULT NULL COMMENT '주소',
        longitude DECIMAL(10, 7) DEFAULT NULL COMMENT '경도',
        latitude DECIMAL(10, 7) DEFAULT NULL COMMENT '위도',
        rating_avg DECIMAL(3, 1) DEFAULT NULL COMMENT '평균 평점 (총합이 아닌 평균)',
        rating_count INTEGER DEFAULT NULL COMMENT '평점 개수',
        contact_number VARCHAR(20) DEFAULT NULL COMMENT '연락처',
        facility_infos JSON DEFAULT NULL COMMENT '시설 정보 (JSON 형식)',
        operation_infos JSON DEFAULT NULL COMMENT '운영 정보 (JSON 형식)',
        operation_times JSON DEFAULT NULL COMMENT '운영 시간 (JSON 형식)',
        bookmark_count INTEGER DEFAULT NULL COMMENT '북마크 개수',
        respresentative_image_url MEDIUMTEXT DEFAULT NULL COMMENT '대표 이미지 URL',
        view_count INTEGER DEFAULT NULL COMMENT '조회수 (상세보기한 횟수)',
        discount_content VARCHAR(255) DEFAULT NULL COMMENT '할인 내용 (예: 성대생 학생할인 등)',
        kakao_rating_avg DECIMAL(3, 1) DEFAULT NULL COMMENT '카카오에서 가져온 평균 평점',
        kakao_rating_count INTEGER DEFAULT NULL COMMENT '카카오에서 가져온 평점 개수',
        menus MEDIUMTEXT DEFAULT NULL COMMENT '메뉴 정보',
        PRIMARY KEY (id)
    )
    """
  )
  cursor.execute(create_table_query)

def create_menus_table(cursor):
  create_table_query = (
    """
    CREATE TABLE IF NOT EXISTS menus (
        id INTEGER NOT NULL AUTO_INCREMENT,
        menu_name VARCHAR(100) NOT NULL COMMENT '메뉴 이름',
        price VARCHAR(20) DEFAULT NULL COMMENT '메뉴 가격',
        description VARCHAR(255) DEFAULT NULL COMMENT '메뉴 설명',
        is_representative BOOLEAN DEFAULT NULL COMMENT '대표 메뉴 여부',
        image_url MEDIUMTEXT DEFAULT NULL COMMENT '메뉴 이미지 URL',
        restaurant_id INTEGER NOT NULL COMMENT '식당 ID',
        PRIMARY KEY (id),
        FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE
    )
    """
  )
  cursor.execute(create_table_query)

def create_restaurant_categories_table(cursor):
  create_table_query = (
    """
    CREATE TABLE IF NOT EXISTS restaurant_categories (
        id INTEGER NOT NULL AUTO_INCREMENT,
        name VARCHAR(100) NOT NULL COMMENT '소분류 이름',
        category_groups VARCHAR(100) NOT NULL COMMENT '대분류',
        PRIMARY KEY (id)
    )
    """
  )
  cursor.execute(create_table_query)

def create_restaurant_category_mapping_table(cursor):
  create_table_query = (
    """
    CREATE TABLE IF NOT EXISTS restaurant_category_mapping (
        id INTEGER NOT NULL AUTO_INCREMENT,
        restaurant_id INTEGER NOT NULL COMMENT '레스토랑 ID',
        category_id INTEGER NOT NULL COMMENT '소분류 ID',
        PRIMARY KEY (id),
        FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES restaurant_categories(id) ON DELETE CASCADE
    )
    """
  )
  cursor.execute(create_table_query)

def create_restaurants_ratings_table(cursor):
  create_table_query = (
    """
    CREATE TABLE IF NOT EXISTS restaurants_ratings
    (
        id            INTEGER AUTO_INCREMENT PRIMARY KEY,
        restaurant_id INTEGER NOT NULL COMMENT '식당 ID',
        user_id       INTEGER NOT NULL COMMENT '유저 ID',
        rating        FLOAT NOT NULL COMMENT '유저 평점 ',
        CONSTRAINT restaurants_ratings_ibfk_1
            FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
                ON DELETE CASCADE
    )
    """
  )
  cursor.execute(create_table_query)
def create_restaurant_bookmark_lists(cursor):
  create_table_query = (
    """
    CREATE TABLE IF NOT EXISTS restaurant_bookmark_lists
    (
        id       INT AUTO_INCREMENT PRIMARY KEY,
        user_id  INT NOT NULL COMMENT '유저 ID',
        CONSTRAINT user_bookmark_lists_ibfk_1
            FOREIGN KEY (user_id) REFERENCES users (id)
            ON DELETE CASCADE
    )
    """
  )
  cursor.execute(create_table_query)
def create_restaurant_bookmark_list_mapping(cursor):
  create_table_query = (
    """
    CREATE TABLE IF NOT EXISTS restaurant_bookmark_list_mapping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    list_id INT NOT NULL COMMENT '북마크 리스트 ID',
    restaurant_id INT NOT NULL COMMENT '식당 ID',
    FOREIGN KEY (list_id) REFERENCES bookmark_lists (id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants (id) ON DELETE CASCADE
    )

    """
  )
  cursor.execute(create_table_query)
def create_restaurant_bookmarks_table(cursor):
  create_table_query = (
    """
    CREATE TABLE IF NOT EXISTS restaurant_bookmarks (
        id INTEGER NOT NULL AUTO_INCREMENT,
        restaurant_id INTEGER NOT NULL COMMENT '식당 ID',
        user_id INTEGER NOT NULL COMMENT '유저 ID',
        PRIMARY KEY (id),
        FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE
    )
    """
  )
  cursor.execute(create_table_query)

if __name__ == "__main__":
  # db_config = {
  #   'host': '127.0.0.1',
  #   'port': 3307,
  #   'user': 'skku-user',
  #   'password': 'skku-pw',
  #   'database': 'skku-practice'
  # }
  db_config = {
    'host': 'mysql',
    'port': 3306,
    'user': 'skku-user',
    'password': 'skku-pw',
    'database': 'skku'
  }

  create_database_tables(db_config)
