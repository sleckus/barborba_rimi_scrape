import time
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models.db import get_db_connection, clear_table, insert_milk_data


def extract_links_mile(driver, xpath):
    link_list = []
    time.sleep(1)
    container = driver.find_element(By.XPATH, xpath)
    list_items = container.find_elements(By.CSS_SELECTOR, '[data-testid="main-productCard"]')
    for item in list_items:
        link = item.find_element(By.TAG_NAME, "a").get_attribute('href')
        print(link)
        link_list.append(link)
    return link_list

def extract_links_mile_bad(driver, xpath):
    link_list = []
    category_list = []
    container_cat = driver.find_element(By.XPATH, "/html/body/div/span[1]/div/div/span/div/div[2]/span[1]/div/div[1]/span/div")
    cat_items = container_cat.find_elements(By.CSS_SELECTOR, 'button[role="button"]')
    for item in cat_items:

        item.click()
        time.sleep(1)

    time.sleep(1)
    container = driver.find_element(By.XPATH, xpath)
    list_items = container.find_elements(By.CSS_SELECTOR, '[data-testid="main-productCard"]')
    for item in list_items:
        link = item.find_element(By.TAG_NAME, "a").get_attribute('href')
        print(link)
        link_list.append(link)
    return link_list


def process_links_mile(driver, link_list, table_name):
    conn = get_db_connection()
    clear_table(conn, table_name)

    for link in link_list:
        print("*" * 30)
        driver.get(link)
        time.sleep(0.5)

        price_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[2]/div/div[3]/div/div[3]/div/div[2]/div[1]/div/div[2]/h1')))
        title = price_element.text.strip()
        print(title)

        price_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="fti-product-price--0"]/div[1]/div[1]')))
        price_text = re.sub(r"[^0-9.,]", "", price_element.text.replace("\n", "").strip()).replace(",", ".")
        print(f"Price: {price_text[:4]} Eur")

        is_sale = False
        if len(price_text) > 4:
            is_sale = True
            print(f'Su nuolaida')

        price_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="fti-product-price--0"]/div[1]/div[2]')))
        price_per = re.sub(r"[^0-9.,]", "", price_element.text.replace("\n", "").strip()).replace(",", ".")
        if len(price_text) > 4:
            price_per = price_text[4:]
        print(f"Price per liter: {price_per} Eur/L")

        try:
            fat_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[2]/div/div[3]/div/div[3]/div/div[3]/div/table/tbody/tr[2]/td[2]')))
            fat_per = re.sub(r"[^0-9.,]", "", fat_element.text.replace("\n", "").strip()).replace(",", ".")
            print(f"Fat percentage: {fat_per} g")
        except Exception as e:
            print(f"Failed to get fat percentage: {e}")
            fat_per = "0"

        volume = float(price_text[:4]) / float(price_per)
        package_size = round(round(volume, 3) * 1000, -2)
        print(f"Package size is: {package_size} milliliters")

        scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert data,.
        insert_milk_data(conn, table_name, title, fat_per, package_size, price_text[:4], price_per, scraped_at, is_sale)
        print("=" * 30)