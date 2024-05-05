from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
import requests

API_KEY = ""
DB_ID = ""
headers = {"Authorization" : "Bearer " + API_KEY,
           "Content-Type" : "application/json",
           "Notion-Version" : "2022-06-28"}




### --- PSN PROFILES SCRAPER --- ###
def psnprofiles_scraper(url):
    driver = webdriver.Firefox()
    driver.get(url)
    sleep(2)

    try:  # Iframe contains cookies so click button there
        iframe = driver.find_element(By.CSS_SELECTOR, "iframe[src='https://cdn.privacy-mgmt.com/index.html?hasCsp=true&message_id=1126540&consentUUID=null&preload_message=true&version=v1']")
        driver.switch_to.frame(iframe)
        button = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[3]/div[2]/button")
        button.click()
        driver.switch_to.default_content()        
    except:
        print('Failure')
        pass

    a = driver.find_elements(By.CLASS_NAME, 'grow') # Detects Tips & Strategies Section being picked up and allows for removal from details
    a = [t.text for t in a]
    if a.index('GUIDE CONTENTS') - a.index('ROADMAP') != 1:  # Extra section can only be between these two
        remove_first = 1
    else:
        remove_first = 0
     
    trophy = driver.find_elements(By.CSS_SELECTOR, "td[style*='padding']") # Gets Trophy Name & Description
    details = driver.find_elements(By.CLASS_NAME, 'section-original')  # Gets Trophy Specific details

    trophy = [t.text for t in trophy]
    details = [d.text for d in details]
    details = details[remove_first:]
    details.insert(0,'Platinum') # Allows Trophy & Details to be same length
       
    game_name = driver.find_element(By.XPATH, '//*[@id="desc-name"]').text
    driver.quit()
    return (trophy, details, game_name)




### --- POWERPYX SCRAPER --- ###
def powerpyx_scraper(url):
    driver = webdriver.Firefox()
    driver.get(url)
    sleep(3)
    
    try:
        button = driver.find_element(By.CLASS_NAME, 'fc-button')  # Handle Cookie button
        button.click() 
    except:
        print('failure')
        pass
    
    trophy = driver.find_elements(By.CSS_SELECTOR, 'tr > td:nth-child(2)')
    details = driver.find_elements(By.CSS_SELECTOR, 'tr > td[colspan="3"]')
    trophy = [t.text for t in trophy]
    details = [d.text for d in details]
    
    game_name = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[3]/main/article/div/h2[1]').text
    driver.quit()
    return (trophy, details, game_name)






### --- CHECK GAME --- ###
def check_game(DB_ID, game_name):  # Check if game_name exists in database
    url = f'https://api.notion.com/v1/databases/{DB_ID}'
    res = requests.get(url, headers=headers)
    db_info = res.json()
    options = db_info['properties']['Game']['select']['options']
    
    games = [game['name'] for game in options]  # Gets all game names
    
    if game_name not in games:
        url = 'https://api.notion.com/v1/pages'
        payload = {"parent": {"database_id": DB_ID},
        "properties": {"Game": {"type": "select", "select": {"name": game_name}}}}
        
        res = requests.post(url, json=payload, headers=headers)   




### --- ADD ROW --- ####
def add_row(DB_ID, data):
    url = f"https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": DB_ID},
        "properties": {
            "Trophy": {"title": [{"text": {"content": data["Trophy"]}}]},
            "Details": {"rich_text": [{"text": {"content": data["Details"]}}]},
            "Notes": {"rich_text": [{"text": {"content": data["Notes"]}}]},
            "Game": {"select": {"name": data["Game"]}}
        }}
    
    for attempt in range(3):
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            print('Succesful')
            return
        else:
            print('Trying Again')
            print(res.status_code)
            sleep(1)




### --- TRACKER ADDER --- ####
def tracker_adder(url, DB_ID):
    if 'powerpyx' in url: # Automatically choses appropriate scraper from url-link
        returned = powerpyx_scraper(url)
    elif 'psnprofiles' in url:
        returned = psnprofiles_scraper(url)
        
        
    trophy_list = [t.split('\n') for t in returned[0]] # Fixes Format
    trophy_list = [t for t in trophy_list if len(t)>1] # Removes irrelevant lists
    trophy_list = [i for i in trophy_list if all(x not in i[0] for x in ['Trophy Guide', 'Collectibles'])]  # Removes Extra pick ups

    details_list = [d.replace('\n', ' ') for d in returned[1]] # Fixes Format

    game_name = returned[2].replace(' Trophy Roadmap', '')  # Ensures only name captured
    game_name = returned[2].replace(' Trophy Guide', '') 
    
    check_game(DB_ID, game_name)
    
    for i in range (0, len(details_list)):
        t, d, n = f'{trophy_list[i][0]}', f'{trophy_list[i][1]}', f'{details_list[i]}'

        new_row = {'Trophy':t, 'Details':d, 'Notes':n[:1999], 'Game':game_name}  # 2000 characters rate limit
        add_row(DB_ID, new_row)



### --- ACTIVATE SCRIPT --- ###
url = ""
tracker_adder(url, DB_ID)




