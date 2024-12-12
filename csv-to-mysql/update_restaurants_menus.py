# update_restaurants_menus.py
import pymysql
import json

def update_restaurants_menus(db_config):
  connection = pymysql.connect(**db_config)
  cursor = connection.cursor()

  try:
    # Get all restaurant IDs
    cursor.execute("SELECT name FROM restaurants")
    restaurant_names = cursor.fetchall()

    for (restaurant_name,) in restaurant_names:
      # Get all menus for the restaurant
      cursor.execute("SELECT menu_name, price, description, is_representative, image_url FROM menus WHERE restaurant_name = %s", (restaurant_name,))
      menus = cursor.fetchall()

      # Prepare menus data in JSON format
      menus_list = []
      for menu in menus:
        menu_data = {
          "menu_name": menu[0],
          "price": menu[1],
          "description": menu[2],
          "is_representative": menu[3],
          "image_url": menu[4]
        }
        menus_list.append(menu_data)

      menus_json = json.dumps(menus_list, ensure_ascii=False)

      # Update the restaurant's menus field
      update_query = "UPDATE restaurants SET menus = %s WHERE name = %s"
      cursor.execute(update_query, (menus_json, restaurant_name))

    # Commit all updates
    connection.commit()
    print("Menus updated successfully for all restaurants.")
  except Exception as e:
    print(f"Error: {e}")
    connection.rollback()
  finally:
    cursor.close()
    connection.close()
