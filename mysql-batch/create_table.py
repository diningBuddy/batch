from delete_table_list import *

def create_table(cursor):
    
    cursor.execute(delete_table_restaurants)
    cursor.execute(delete_table_categories)
    cursor.execute(delete_table_restaurant_categories)
    cursor.execute(delete_table_menus)
    
