from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from time import sleep
import requests, time
START = time.time()

options = Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"



API_KEY = ""
DB_ID = ""
headers = {
    "Authorization" : "Bearer " + API_KEY,
    "Content-Type" : "application/json",
    "Notion-Version" : "2022-06-28"}






def info_Cleaner(trophy, game_name, TYPE, details):
    trophy_list = [t.split('\n', maxsplit=1) for t in trophy]  # Split by first \n
    trophy_list = [t for t in trophy_list if len(t)>1]  # Remove irrelevant lists
    trophy_list = [i for i in trophy_list if all(x not in i[0] for x in ['Trophy Guide', 'Collectibles', 'Walkthrough', '100%'])]  # Remove irrelevant Extas
    
    game_name = game_name
    for x in [' Trophy Roadmap', ' Trophy Guide', ' Trophies']:
        game_name = game_name.replace(x, '')
               
    if TYPE == 2:  # --- Cuts details down so can be added into Notion
        details_list = [d.replace('\n', ' ')[:1500] for d in details]
    return (trophy_list, game_name, TYPE, details_list) 


# -------------------- PSNPROFILES SCRAPER -------------------- #
def checkSections(driver, details):
    """Detects Tips & Strategies section and removes it from details if present"""
    sections = driver.find_elements(By.CLASS_NAME, 'grow')
    sections = [t.text for t in sections]
           
    try:
        details = details[1:] if a.index('GUIDE CONTENTS') - a.index('ROADMAP') !=1 else details  # If the difference between these is not 1 then something else is present
        details.insert(0, ' ')
    except:
        pass
    return details
    

def psnprofiles_Scraper(URL):
    """Handles both psnprofile cases: Guide Attached, Raw list of Trophies"""
    TYPE = 2 if 'guide' in URL else 1
    driver = webdriver.Firefox(options=options)
    driver.get(URL)
    sleep(3)
    
    # ---------- HANDLE COOKIE POPUP ---------- #
    iframe = driver.find_element(By.CSS_SELECTOR, "iframe[src='https://cdn.privacy-mgmt.com/index.html?hasCsp=true&message_id=1140375&consentUUID=null&consent_origin=https%3A%2F%2Fcdn.privacy-mgmt.com%2Fconsent%2Ftcfv2&preload_message=true&version=v1']")
    driver.switch_to.frame(iframe)
    button = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[3]/div[2]/button[1]')
    button.click()
    driver.switch_to.default_content()
    
    if TYPE == 1:  # --- Just a list of Trophies no Guide attached
        trophy = driver.find_elements(By.CSS_SELECTOR, "td[style='width: 100%;']")
        trophy = [t.text for t in trophy]
        details = None
        game_name = driver.find_element(By.XPATH, '/html/body/div[4]/div[3]/div/div[2]/div[1]/div[2]').text.title()
        
    if TYPE == 2:  # --- Where the Guide is attached too
        trophy = driver.find_elements(By.CSS_SELECTOR, "td[style*='padding']")  # Retreives TrophyName & Desc
        details = driver.find_elements(By.CLASS_NAME, 'section-original')  # Retreives Guide Info
        trophy = [t.text for t in trophy]
        details = [d.text[:1500] for d in details]
        game_name = driver.find_element(By.XPATH, '//*[@id="desc-name"]').text
    
    driver.quit()
    return info_Cleaner(trophy, game_name, TYPE, details)


# -------------------- POWERPYX SCRAPER -------------------- #
def powerpyx_Scraper(URL):
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    sleep(3)
    
    # ---------- HANDLE COOKIE POPUP ---------- #
    button = driver.find_element(By.CLASS_NAME, 'fc-button')
    button.click()
    
    trophy = driver.find_elements(By.CSS_SELECTOR, 'tr > td:nth-child(2)')
    details = driver.find_elements(By.CSS_SELECTOR, 'tr > td[colspan="3"]')
    trophy = [t.text for t in trophy]
    details = [d.text for d in details]
    game_name = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[3]/main/article/div/h2[1]').text

    driver.quit()
    return info_Cleaner(trophy, game_name, 2, details)






def check_game(DB_ID, game):
    """If Game not in Notion list, automatically add it in"""
    res = requests.get(f'https://api.notion.com/v1/databases/{DB_ID}', headers=headers)
    games = res.json()['properties']['Game']['select']['options']
    games = [g['name'] for g in games]  # -- Get list of Games
    
    if game not in games:
        payload = {"parent": {"database_id": DB_ID}, "properties": {"Game": {"type": "select", "select": {"name": game}}}}        
        res = requests.post('https://api.notion.com/v1/pages', json=payload, headers=headers)    
        print('Added new Game into List')    


def add_row(DB_ID, VALS, TYPE):
    # ---------- PAYLOAD CREATION ---------- #
    payload = {
        "parent": {"database_id": DB_ID},
        "properties": {
            "Trophy": {"title": [{"text": {"content": VALS["Trophy"]}}]},
            "Details": {"rich_text": [{"text": {"content": VALS["Details"]}}]}
        }} 
    if TYPE == 2:  # We only add 'Notes' into payload if 'Details' actually exists
        payload['properties']['Notes'] = {"rich_text": [{"text": {"content": VALS["Notes"]}}]}
    payload['properties']['Game'] = {"select": {"name": VALS["Game"]}}

    requests.post(f"https://api.notion.com/v1/pages", json=payload, headers=headers)
    print('Row Succesfully Added')






# -------------------- SCRIPT ACTIVATION -------------------- #
URL = '<URL-HERE>'
if 'powerpyx' in URL:
    info = powerpyx_Scraper(URL)
else:
    info = psnprofiles_Scraper(URL)  # Note, the non-guide version here works for both powerpyx/psnprofiles


length, data = len(info[0]), {} # -- length of TrophyList
for i in range(0, length):
    data[i] = {'Trophy': info[0][i][0],
               'Details': info[0][i][1]}
    if info[2] == 2:  # We only add 'Notes' into dictionary if 'Details' actually exists
        data[i]['Notes'] = info[3][i]
    data[i]['Game'] = info[1]
    
check_game(DB_ID, info[1])

i=0
for KEY, VALS in data.items():
    if i == 3:
        i = 0
        sleep(1)
    add_row(DB_ID, VALS, info[2])
