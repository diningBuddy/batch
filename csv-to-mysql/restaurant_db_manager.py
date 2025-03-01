# restaurant_db_manager.py
import insert_restaurants
import insert_menus
import update_restaurants_menus
import insert_categories
import insert_category_mapping
import update_restaurant_ranks

def main():

  db_config = {
    'host': 'mysql',
    'port': 3306,
    'user': 'skku-user',
    'password': 'skku-pw',
    'database': 'skku'
  }

  restaurants_csv_file_path = 'kakao_restaurants.csv'
  insert_restaurants.insert_restaurants(db_config, restaurants_csv_file_path)

  menus_csv_file_path = 'kakao_menus.csv'
  insert_menus.insert_menus(db_config, menus_csv_file_path)

  categories_txt_file_path = 'kakao_categories.txt'
  insert_categories.insert_categories(db_config, categories_txt_file_path)

  update_restaurants_menus.update_restaurants_menus(db_config)

  insert_category_mapping.insert_category_mapping(db_config)

  kakao_map_ranks_csv_file_path = 'restaurant-rank/kakao_map_ranks.csv'
  update_restaurant_ranks.insert_ranks(db_config, kakao_map_ranks_csv_file_path)

if __name__ == "__main__":
  main()
