from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def disCookies(driver):
    try:
        wait = WebDriverWait(driver, 10)
        cookie_accept_button = wait.until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll"))
        )
        cookie_accept_button.click()
        print("Cookie dismissed.")
    except Exception as e:
        print(f"Error dismissing cookies: {e}")
