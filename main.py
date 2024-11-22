import time
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models.db import get_db_connection, clear_table, insert_milk_data

def disCookies(driver):
    try:
        wait = WebDriverWait(driver, 10)
        cookie_accept_button = wait.until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll"))
        )
        cookie_accept_button.click()
        print("Cookie prompt dismissed.")
    except Exception as e:
        print(f"Cookie prompt not found: {e}")

driver = webdriver.Chrome()
driver.maximize_window()
driver.implicitly_wait(5)
driver.get("https://www.barbora.lt/pieno-gaminiai-ir-kiausiniai/pienas/pasterizuotas-pienas")

disCookies(driver)

link_list = []
time.sleep(1)
container = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[3]/div/div[3]/div[2]/div/ul')
list_items = container.find_elements(By.TAG_NAME, 'li')
for item in list_items:
    link = item.find_element(By.TAG_NAME, "a").get_attribute('href')
    print(link)
    link_list.append(link)

conn = get_db_connection()
clear_table(conn, "maxima_milk")

for link in link_list:
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
        print(f"Failed to get fat percentage from the page: {e}")

    volume = float(price_text[:4]) / float(price_per)
    package_size = round(round(volume, 3) * 1000, -2)
    print(f"Package size is: {package_size} milliliters")

    scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    insert_milk_data(conn, title, fat_per, package_size, price_text, price_per, scraped_at)
    package_size = 0
    fat_per = 0
    price_per = 0
    price_text = 0
    print("=" * 30)


driver.quit()
conn.close()
