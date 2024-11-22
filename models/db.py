import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="127.0.0.1",  # local
        user='root',
        password='',
        database="supermarkets"
    )
    return conn

def clear_table(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name}")
    cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1")  #
    conn.commit()
    cursor.close()
    print(f"Table {table_name} cleared and reset.")

def insert_milk_data(conn, table_name, name, fat_content, package_size, price, price_per_kg, scraped_at, is_sale):
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO {table_name} (name, fat_content, package_size, price, price_per_kg, scraped_at, is_sale) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (name, fat_content, package_size, price, price_per_kg, scraped_at, is_sale)
    )

    conn.commit()
    cursor.close()
    print(f"Data inserted into {table_name}.")
