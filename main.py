import string

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from functools import reduce
import operator
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

MATCH_URL = 'https://liga.99damage.de/leagues/matches/921095-team-stetiix-vs-illusion-esports-team-reality'
BASE_URL = 'https://liga.99damage.de'
OWN_TEAM_NAME = 'illusion-esports-team-reality'

def main():
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))

    accept_gta(driver, BASE_URL)
    opponent_url, opponent_abbr = get_opponent_match_page_from_match_page(driver, MATCH_URL, OWN_TEAM_NAME)
    match_links = get_opponent_match_links(driver, opponent_url)
    
    matches = []
    for match_link in match_links:
        match_data = get_match_data(driver, match_link, opponent_abbr)
        match_data and matches.append(match_data)

    driver.quit()

    save_to_pdf(opponent_abbr, getMaps(matches, 'banns'), 'banns')
    save_to_pdf(opponent_abbr, getMaps(matches, 'picks'), 'picks')


def accept_gta(driver: WebDriver, page_url: string):
    driver.get(page_url)
    element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'uc-btn-accept-banner'))
        )
    element.click()

def get_opponent_match_page_from_match_page(driver: WebDriver, match_url: string, own_team_name: string):
    driver.get(match_url)
    opponent_buttons = driver.find_elements(by=By.CLASS_NAME, value='image-present')
    [team for team in opponent_buttons if own_team_name not in team.get_attribute('href')][0].click()
    opponent_abbr = (driver.find_element(by=By.CLASS_NAME, value='page-title').text).split('(')[-1][:-1]
    return (driver.current_url, opponent_abbr)

def get_opponent_match_links(driver: WebDriver, opponent_url):
    driver.get(opponent_url)
    a_tags = [element.find_elements(by=By.CLASS_NAME, value='table-cell-container') for element in driver.find_elements(by=By.CLASS_NAME, value='league-team-stage')]
    a_tags = reduce(operator.concat, a_tags)
    a_tags =  [a_tag.get_attribute('href') for a_tag in a_tags]
    return list(set(a_tags))

def get_match_data(driver: WebDriver, match_link: string, opponent_abbr: string):
    driver.get(match_link)
    try:
        WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'league-match-draft-log'))
            )
    except:
        return None
    voting_log = driver.find_element(by=By.CLASS_NAME, value='league-match-draft-log')
    votings = voting_log.find_elements(by=By.TAG_NAME, value='li')
    votings = [voting.text for voting in votings]
    if len([voting for voting in votings if 'Bann' in voting.split(' ')]) > 4:
        return
    banns = [voting.split(' ')[-1] for voting in votings if 'Bann' in voting.split(' ') and opponent_abbr in voting.split(' ')]
    picks = [voting.split(' ')[-1] for voting in votings if 'Pick' in voting.split(' ') and opponent_abbr in voting.split(' ')]
    played = [voting.split(' ')[-1] for voting in votings if 'Pick' in voting.split(' ')]
    scores = driver.find_element(by=By.CLASS_NAME, value='txt-info').text.split(' / ')
    first_named = ' '.join(votings[0].split(' ')[:-2]) == opponent_abbr
    return {
        'opponent': ' '.join(votings[0].split(' ')[:-2]) if not first_named else ' '.join(votings[1].split(' ')[:-2]),
        'banns': banns,
        'picks': picks,
        'played': [
        {
            'map': played[0],
            'won': int(scores[0].split(':')[0]) > int(scores[0].split(':')[1]) if first_named else int(scores[0].split(':')[0]) < int(scores[0].split(':')[1]),
            'score': scores[0]
        },
        {
            'map': played[1],
            'won': int(scores[1].split(':')[0]) > int(scores[1].split(':')[1]) if first_named else int(scores[1].split(':')[0]) < int(scores[1].split(':')[1]),
            'score': scores[1]
        }],
    }

def getMaps(matches, key: string):
    maps = {}
    for match in matches:
        for item in match[key]:
            if item in maps:
                maps[item] += 1
            else:
                maps[item] = 1
    return pd.DataFrame([maps])

def save_to_pdf(opponent_abbr: string, df: pd.DataFrame, file_name: string):
    #https://stackoverflow.com/questions/32137396/how-do-i-plot-only-a-table-in-matplotlib
    fig, ax =plt.subplots(figsize=(12,4))
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')

    #https://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot
    pp = PdfPages(opponent_abbr + "_" + file_name + ".pdf")
    pp.savefig(fig, bbox_inches='tight')
    pp.close()

if __name__ == '__main__':
    main()
