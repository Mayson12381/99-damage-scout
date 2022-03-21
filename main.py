import time
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

MATCH_URL = 'https://liga.99damage.de/leagues/matches/921095-team-stetiix-vs-illusion-esports-team-reality'
BASE_URL = 'https://liga.99damage.de'
OWN_TEAM_NAME = 'illusion-esports-team-reality'

def main():
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))

    accept_gta(driver, BASE_URL)
    opponent_url = get_opponent_match_page_from_match_page(driver, MATCH_URL, OWN_TEAM_NAME)
    print(opponent_url)

    time.sleep(5)
    driver.quit()

def accept_gta(driver: WebDriver, page_url):
    driver.get(page_url)
    element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'uc-btn-accept-banner'))
        )
    element.click()

def get_opponent_match_page_from_match_page(driver: WebDriver, match_url, own_team_name):
    driver.get(match_url)
    opponent_buttons = driver.find_elements(by=By.CLASS_NAME, value='image-present')
    [team for team in opponent_buttons if own_team_name not in team.get_attribute('href')][0].click()
    return driver.current_url

if __name__ == '__main__':
    main()