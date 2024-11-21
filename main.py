import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector


def connectDB():
    conn = mysql.connector.connect(
        host="127.0.0.1",  # local
        user='root',
        password='',
        database="supermarkets"
    )
    return conn

def disCookies(driver):
    try:
        wait = WebDriverWait(driver, 10)
        cookie_accept_button = wait.until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll"))
        )
        cookie_accept_button.click()
        print("Cookie prompt dismissed.")
    except Exception as e:
        print(f"Cookie prompt not found or could not be dismissed: {e}")


driver = webdriver.Chrome()
driver.maximize_window()
driver.implicitly_wait(5)
driver.get("https://www.barbora.lt/pieno-gaminiai-ir-kiausiniai/pienas/pasterizuotas-pienas")

disCookies(driver)

link_list = []
time.sleep(2)
container = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[3]/div/div[3]/div[2]/div/ul')
list_items = container.find_elements(By.TAG_NAME, 'li')
for item in list_items:
    link = item.find_element(By.TAG_NAME,"a").get_attribute('href')
    print(link)
    link_list.append(link)

for link in link_list:
    driver.get(link)

    time.sleep(50)



