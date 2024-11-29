import time
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models.db import get_db_connection, clear_table, insert_milk_data


class BarboraExtractor:
    def __init__(self, driver, table_name):
        self.driver = driver
        self.table_name = table_name
        self.conn = get_db_connection()

    def extract_links(self, xpath):
        link_list = []
        time.sleep(1)
        container = self.driver.find_element(By.XPATH, xpath)
        list_items = container.find_elements(By.TAG_NAME, 'li')
        for item in list_items:
            link = item.find_element(By.TAG_NAME, "a").get_attribute('href')
            print(link)
            link_list.append(link)
        return link_list

    def process_links(self, link_list):
        clear_table(self.conn, self.table_name)

        for link in link_list:
            print("*" * 30)
            self.driver.get(link)
            time.sleep(0.5)

            title = self._extract_title()
            price_text, is_sale = self._extract_price()
            price_per = self._extract_price_per(price_text)
            fat_per = self._extract_fat_percentage()
            package_size = self._calculate_package_size(price_text, price_per)
            scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            insert_milk_data(
                self.conn, self.table_name, title, fat_per, package_size, price_text[:4], price_per, scraped_at, is_sale
            )
            print("=" * 30)

    def _extract_title(self):
        try:
            price_element = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[2]/div/div[3]/div/div[3]/div/div[2]/div[1]/div/div[2]/h1')
                )
            )
            raw_title = price_element.text.strip()
            title = re.findall(r'\b[A-Z]+\b', raw_title)
            if not title:
                return raw_title
            return ' '.join(title)
        except Exception as e:
            print(f"Failed to extract title: {e}")
            return "Unknown"

    def _extract_price(self):
        try:
            price_element = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="fti-product-price--0"]/div[1]/div[1]'))
            )
            price_text = re.sub(r"[^0-9.,]", "", price_element.text.replace("\n", "").strip()).replace(",", ".")
            print(f"Price: {price_text[:4]} Eur")
            is_sale = len(price_text) > 4
            if is_sale:
                print("Su nuolaida")
            return price_text, is_sale
        except Exception as e:
            print(f"Failed to extract price: {e}")
            return "0", False

    def _extract_price_per(self, price_text):
        try:
            price_element = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="fti-product-price--0"]/div[1]/div[2]'))
            )
            price_per = re.sub(r"[^0-9.,]", "", price_element.text.replace("\n", "").strip()).replace(",", ".")
            if len(price_text) > 4:
                price_per = price_text[4:]
            print(f"Price per liter: {price_per} Eur/L")
            return price_per
        except Exception as e:
            print(f"Failed to extract price per liter: {e}")
            return "0"

    def _extract_fat_percentage(self):
        try:
            fat_element = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[2]/div/div[3]/div/div[3]/div/div[3]/div/table/tbody/tr[2]/td[2]')
                )
            )
            fat_per = re.sub(r"[^0-9.,]", "", fat_element.text.replace("\n", "").strip()).replace(",", ".")
            print(f"Fat percentage: {fat_per} g")
            return fat_per
        except Exception as e:
            print(f"Failed to extract fat percentage: {e}")
            return "0"

    def _calculate_package_size(self, price_text, price_per):
        try:
            volume = float(price_text[:4]) / float(price_per)
            package_size = round(round(volume, 3) * 1000, -2)
            print(f"Package size is: {package_size} milliliters")
            return package_size
        except Exception as e:
            print(f"Failed to calculate package size: {e}")
            return 0

    def close_connection(self):
        self.conn.close()
