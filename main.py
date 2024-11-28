import time
from datetime import datetime
import re

from cffi.cffi_opcode import CLASS_NAME
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models.db import get_db_connection, clear_table, insert_milk_data
from models.cookies import disCookies
from selenium import webdriver
from models.barbora_extractor import extract_links, process_links
from models.lastmile_extractor import extract_links_mile, process_links_mile, extract_links_mile_bad
from models.milk_comparison import MilkComparison

comparison = MilkComparison('maxima_milk', 'iki_milk', 'milk_compare')
comparison.clear_comparison_table()

table_name = 'maxima_milk'
starting_website = 'https://www.barbora.lt/pieno-gaminiai-ir-kiausiniai/pienas/pasterizuotas-pienas'

driver = webdriver.Chrome()
driver.maximize_window()
driver.implicitly_wait(5)
driver.get(starting_website)

conn = get_db_connection()
clear_table(conn, "maxima_milk")

disCookies(driver,By.ID,"CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll")

link_list = extract_links(driver,'/html/body/div[3]/div/div[3]/div/div[3]/div[2]/div/ul')
process_links(driver, link_list, table_name)

table_name = 'iki_milk'
starting_website = 'https://lastmile.lt/chain/category/IKI/Pienas-B7UTvIzcguAYSjSplM0z'
driver = webdriver.Chrome()
driver.maximize_window()
driver.implicitly_wait(5)
driver.get(starting_website)
# sausainiaii
time.sleep(0.69)
disCookies(driver,By.XPATH,"/html/body/div/span[7]/div/span/div/div/div[2]/span[3]/span/button")
# disCookies(driver,By.XPATH,"/html/body/span[2]/div/span/span/span/div/div/div/span/dialog/span/div/span[2]/div/span/button/svg")
time.sleep(1)
all_milk = extract_links_mile(driver,'/html/body/div/span[1]/div/div/span/div/div[2]/span[1]/div/div[2]')
bad_milk = extract_links_mile_bad(driver,'/html/body/div/span[1]/div/div/span/div/div[2]/span[1]/div/div[2]')
link_list = [link for link in all_milk if link not in bad_milk]
print(link_list)
process_links_mile(driver, link_list, table_name)


milk_comparator = MilkComparison(
    maxima_table='maxima_milk',
    iki_table='iki_milk',
    compare_table='milk_compare'
)



milk_comparator.compare_and_store()

milk_comparator.close()

