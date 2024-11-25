import time
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models.db import get_db_connection, clear_table, insert_milk_data
from models.cookies import disCookies
from selenium import webdriver
from models.barbora_extractor import extract_links, process_links


table_name = 'maxima_milk'
starting_website = 'https://www.barbora.lt/pieno-gaminiai-ir-kiausiniai/pienas/pasterizuotas-pienas'

driver = webdriver.Chrome()
driver.maximize_window()
driver.implicitly_wait(5)
driver.get(starting_website)

disCookies(driver)

link_list = extract_links(driver,'/html/body/div[3]/div/div[3]/div/div[3]/div[2]/div/ul')
process_links(driver, link_list, table_name)

conn = get_db_connection()
clear_table(conn, "maxima_milk")




