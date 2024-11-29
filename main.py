import time
from selenium import webdriver
from selenium.webdriver.common.by import By

from models.cookies import disCookies
from models.barbora_extractor import BarboraExtractor
from models.lastmile_extractor import LastMileExtractor
from models.milk_comparison import MilkComparison

comparison = MilkComparison('maxima_milk', 'iki_milk', 'milk_compare')
comparison.clear_comparison_table()

driver = webdriver.Chrome()
driver.maximize_window()
driver.implicitly_wait(5)


table_name = 'maxima_milk'
starting_website = 'https://www.barbora.lt/pieno-gaminiai-ir-kiausiniai/pienas/pasterizuotas-pienas'
driver.get(starting_website)

disCookies(driver, By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll")

barbora_extractor = BarboraExtractor(driver, table_name)
link_list = barbora_extractor.extract_links('/html/body/div[3]/div/div[3]/div/div[3]/div[2]/div/ul')
barbora_extractor.process_links(link_list)
barbora_extractor.close_connection()


###################################################
driver = webdriver.Chrome()
driver.maximize_window()
driver.implicitly_wait(5)

table_name = 'iki_milk'
starting_website = 'https://lastmile.lt/chain/category/IKI/Pienas-B7UTvIzcguAYSjSplM0z'
driver.get(starting_website)

extractor = LastMileExtractor(driver, table_name)

button_xpaths = [
    '/html/body/div/span[1]/div/div/span/div/div[2]/span[1]/div/div[1]/span/div/span[2]/span/button/span/span',
    '/html/body/div/span[1]/div/div/span/div/div[2]/span[1]/div/div[1]/span/div/span[3]/span/button/span/span',
    '/html/body/div/span[1]/div/div/span/div/div[2]/span[1]/div/div[1]/span/div/span[4]/span/button/span/span',
    '/html/body/div/span[1]/div/div/span/div/div[2]/span[1]/div/div[1]/span/div/span[5]/span/button/span/span',
    '/html/body/div/span[1]/div/div/span/div/div[2]/span[1]/div/div[1]/span/div/span[6]/span/button/span/span'
]

time.sleep(0.69)
disCookies(driver, By.XPATH, "/html/body/div/span[7]/div/span/div/div/div[2]/span[3]/span/button")

all_links = extractor.extract_links('/html/body/div/span[1]/div/div/span/div/div[2]/span[1]/div/div[2]')
bad_links = extractor.extract_bad_links('/html/body/div/span[1]/div/div/span/div/div[2]/span[1]/div/div[2]', button_xpaths)
valid_links = [link for link in all_links if link not in bad_links]

extractor.process_links(valid_links)
print(link_list)



milk_compare = MilkComparison(
    maxima_table='maxima_milk',
    iki_table='iki_milk',
    compare_table='milk_compare'
)



milk_compare.compare_and_store()

milk_compare.close()

