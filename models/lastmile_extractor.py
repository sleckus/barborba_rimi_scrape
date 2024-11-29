import time
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models.db import get_db_connection, clear_table, insert_milk_data


class LastMileExtractor:
    def __init__(self, driver, table_name):
        self.driver = driver
        self.table_name = table_name
        self.conn = get_db_connection()

    def clear_table(self):
        clear_table(self.conn, self.table_name)

    def extract_links(self, xpath):
        link_list = []
        time.sleep(1)
        container = self.driver.find_element(By.XPATH, xpath)
        list_items = container.find_elements(By.CSS_SELECTOR, '[data-testid="main-productCard"]')
        for item in list_items:
            link = item.find_element(By.TAG_NAME, "a").get_attribute('href')
            print(link)
            link_list.append(link)
        return link_list

    def extract_bad_links(self, xpath, button_xpaths):
        bad_link_list = []
        for button_xpath in button_xpaths:
            self.driver.find_element(By.XPATH, button_xpath).click()
            time.sleep(1)
            container = self.driver.find_element(By.XPATH, xpath)
            list_items = container.find_elements(By.CSS_SELECTOR, '[data-testid="main-productCard"]')
            for item in list_items:
                link = item.find_element(By.TAG_NAME, "a").get_attribute('href')
                print(link)
                bad_link_list.append(link)
        return bad_link_list

    def process_links(self, link_list):
        self.clear_table()

        for link in link_list:
            print("*" * 30)
            self.driver.get(link)
            time.sleep(1)

            try:
                raw_title = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div/span[1]/div/div/span/div/div[2]/div[2]/div[1]/div[2]/div/div[1]/span[2]/span')
                    )
                ).text.strip()
                title = re.findall(r'\b[A-Z]+\b', raw_title)
                title = ' '.join(title) if title else raw_title
                print(title)

                price_text = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div/span[1]/div/div/span/div/div[2]/div[2]/div[1]/div[2]/div/div[3]/div/div/span/span')
                    )
                ).text.strip()
                price_text = re.sub(r"[^0-9.,]", "", price_text.replace("\n", "")).replace(",", ".")
                print(f"Price: {price_text[:4]} Eur")

                is_sale = len(price_text) > 4
                if is_sale:
                    print(f'Su nuolaida')

                price_per = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div/span[1]/div/div/span/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div/span/span/span')
                    )
                ).text.strip()
                price_per = re.sub(r"[^0-9.,]", "", price_per.replace("\n", "")).replace(",", ".")
                print(f"Price per liter: {price_per} Eur/L")

                try:
                    fat_per = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '/html/body/div/span[1]/div/div/span/div/div[2]/div[2]/div[3]/div[2]/span[7]/div/div/span[2]/span/div/div[2]/span[2]/span')
                        )
                    ).text.strip()
                    fat_per = re.sub(r"[^0-9.,]", "", fat_per.replace("\n", "")).replace(",", ".")
                    print(f"Fat percentage: {fat_per} g")
                except Exception as e:
                    print(f"Failed to get fat percentage: {e}")
                    fat_per = "0"

                volume = float(price_text[:4]) / float(price_per)
                package_size = round(round(volume, 3) * 1000, -2)
                print(f"Package size is: {package_size} milliliters")

                scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                insert_milk_data(
                    self.conn, self.table_name, title, fat_per, package_size, price_text[:4], price_per, scraped_at, is_sale
                )
                print("=" * 30)
            except Exception as e:
                print(f"Failed to process link {link}: {e}")
