from datetime import datetime
from models.db import get_db_connection

class MilkComparison:
    def __init__(self, maxima_table, iki_table, compare_table):
        self.maxima_table = maxima_table
        self.iki_table = iki_table
        self.compare_table = compare_table
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()

    def clear_comparison_table(self):
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        self.cursor.execute(f"TRUNCATE TABLE {self.compare_table}")
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print(f"Table {self.compare_table} cleared.")

    def find_matches(self):
        query = f"""
        SELECT 
            m.id AS maxima_id, 
            i.id AS iki_id, 
            m.price AS maxima_price, 
            i.price AS iki_price
        FROM 
            {self.maxima_table} m
        INNER JOIN 
            {self.iki_table} i
        ON 
            m.fat_content = i.fat_content AND 
            m.package_size = i.package_size
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def insert_matches(self, matches):
        insert_query = f"""
        INSERT INTO {self.compare_table} (maxima_id, iki_id, maxima_price, iki_price, price_difference, matched_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        for match in matches:
            maxima_id, iki_id, maxima_price, iki_price = match
            price_difference = abs(float(maxima_price) - float(iki_price))
            matched_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(insert_query, (maxima_id, iki_id, maxima_price, iki_price, price_difference, matched_at))

    def compare_and_store(self):
        matches = self.find_matches()
        self.insert_matches(matches)
        self.conn.commit()
        print("Comparison completed and data stored.")

    def close(self):
        self.cursor.close()
        self.conn.close()
