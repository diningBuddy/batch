# restaurant_db_manager.py
import insert_restaurants
import insert_menus
import update_restaurants_menus
import insert_categories
import insert_category_mapping

def main():
  # db_config = {
  #   'host': '127.0.0.1',
  #   'port': 3307,
  #   'user': 'skku-user',
  #   'password': 'skku-pw',
  #   'database': 'skku-practice'
  # } local

  db_config = {
    'host': 'mysql',
    'port': 3306,
    'user': 'skku-user',
    'password': 'skku-pw',
    'database': 'skku'
  }

  # Insert data into restaurants table
  restaurants_csv_file_path = 'kakao_restaurants.csv'
  insert_restaurants.insert_restaurants(db_config, restaurants_csv_file_path)

  # Insert data into menus table
  menus_csv_file_path = 'kakao_menus.csv'
  insert_menus.insert_menus(db_config, menus_csv_file_path)

  # Insert data into categories table
  categories_txt_file_path = 'kakao_categories.txt'
  insert_categories.insert_categories(db_config, categories_txt_file_path)

  # # Update restaurants' menus field with menus data in JSON format
  update_restaurants_menus.update_restaurants_menus(db_config)

  # Insert restaurant-category mappings
  insert_category_mapping.insert_category_mapping(db_config)


if __name__ == "__main__":
  main()
