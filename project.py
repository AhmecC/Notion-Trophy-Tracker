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






### --- PSN PROFILES TROPHY_LIST SCRAPER --- ###
def trophy_scraper(url):
    driver = webdriver.Firefox()
    driver.get(url)
    sleep(2)
    
    iframe = driver.find_element(By.CSS_SELECTOR, "iframe[src='https://cdn.privacy-mgmt.com/index.html?hasCsp=true&message_id=1140375&consentUUID=null&consent_origin=https%3A%2F%2Fcdn.privacy-mgmt.com%2Fconsent%2Ftcfv2&preload_message=true&version=v1']")
    driver.switch_to.frame(iframe)  # Cookies in Iframe, so we switch to this
    button = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[3]/div[2]/button[1]')
    button.click()  # Click button inside Iframe
    driver.switch_to.default_content()
    
    trophy = driver.find_elements(By.CSS_SELECTOR, "td[style='width: 100%;']")
    trophy = [t.text for t in trophy]  # No Details gathered in this scenario

    game_name = driver.find_element(By.XPATH, '/html/body/div[4]/div[3]/div/div[2]/div[1]/div[2]').text.title()
    driver.quit()
    return (trophy, game_name, 1)




### --- PSN PROFILES SCRAPER --- ###
def psnprofiles_scraper(url):
    driver = webdriver.Firefox()
    driver.get(url)
    sleep(2)
        
    iframe = driver.find_element(By.CSS_SELECTOR, "iframe[src='https://cdn.privacy-mgmt.com/index.html?hasCsp=true&message_id=1140375&consentUUID=null&consent_origin=https%3A%2F%2Fcdn.privacy-mgmt.com%2Fconsent%2Ftcfv2&preload_message=true&version=v1']")  # Might have to change this link
    driver.switch_to.frame(iframe)  # Cookies in Iframe, so we switch to this
    button = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[3]/div[2]/button[1]")
    button.click()  # Click button in Iframe
    driver.switch_to.default_content()
     
    trophy = driver.find_elements(By.CSS_SELECTOR, "td[style*='padding']")  # Gets Trophy Name & Description
    details = driver.find_elements(By.CLASS_NAME, 'section-original')  # Gets Trophy Specific Guide
    trophy = [t.text for t in trophy]
    details = [d.text[:1500] for d in details]    
    
    a = driver.find_elements(By.CLASS_NAME, 'grow')  # Detects Tips & Strategies section and removes it from details
    a = [t.text for t in a]
    try:
        details = details[1:] if a.index('GUIDE CONTENTS') - a.index('ROADMAP') !=1 else details
        details.insert(0, ' ')  # Outside to ensure no errors
    except:
        pass
    
    game_name = driver.find_element(By.XPATH, '//*[@id="desc-name"]').text
    driver.quit()
    return (trophy, game_name, 2, details)




### --- POWERPYX SCRAPER --- ###
def powerpyx_scraper(url):
    driver = webdriver.Firefox()
    driver.get(url)
    sleep(3)
    
    button = driver.find_element(By.CLASS_NAME, 'fc-button')  # Handle Cookie button
    button.click()
    
    trophy = driver.find_elements(By.CSS_SELECTOR, 'tr > td:nth-child(2)')
    details = driver.find_elements(By.CSS_SELECTOR, 'tr > td[colspan="3"]')
    trophy = [t.text for t in trophy]
    details = [d.text for d in details]
    
    game_name = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[3]/main/article/div/h2[1]').text
    driver.quit()
    return (trophy, game_name, 2, details)






### --- ADDING INTO NOTION --- ###
def tracker_adder(url, DB_ID): 
    check_game(DB_ID, game_name)
    
    for key in data:
        add_row(DB_ID, data[key])


### --- CHECK GAME NAME EXISTS IN NOTION --- ###
def check_game(DB_ID, game_name):  # Check if game_name exists
    res = requests.get(f'https://api.notion.com/v1/databases/{DB_ID}', headers=headers)
    db_info = res.json()
    options = db_info['properties']['Game']['select']['options']
    
    games = [game['name'] for game in options]  # Gets all game names
    
    if game_name not in games:
        payload = {"parent": {"database_id": DB_ID},
        "properties": {"Game": {"type": "select", "select": {"name": game_name}}}}
        res = requests.post('https://api.notion.com/v1/pages', json=payload, headers=headers)        


### --- ADD ROW --- ####
def add_row(DB_ID, data):
    if returned[2] == 2:  # 2 Means that Notes are gathered and need to be submitted
        payload = {        
            "parent": {"database_id": DB_ID},
            "properties": {
                "Trophy": {"title": [{"text": {"content": data["Trophy"]}}]},
                "Details": {"rich_text": [{"text": {"content": data["Details"]}}]},
                "Notes": {"rich_text": [{"text": {"content": data["Notes"]}}]},
                "Game": {"select": {"name": data["Game"]}}
            }}
    elif returned[2] == 1:  # No Notes so can omit here
        payload = {        
            "parent": {"database_id": DB_ID},
            "properties": {
                "Trophy": {"title": [{"text": {"content": data["Trophy"]}}]},
                "Details": {"rich_text": [{"text": {"content": data["Details"]}}]},
                "Game": {"select": {"name": data["Game"]}}
            }}

        
    for attempt in range(3):
        res = requests.post(f"https://api.notion.com/v1/pages", json=payload, headers=headers)
        if res.status_code == 200:
            print('Succesful')
            return
        else:
            print('Trying Again')
            print(res.status_code)
            sleep(1)




### --- TRACKER ADDER --- ####
url = ''

if 'powerpyx' in url and 'guide' in url: # Automatically choses appropriate scraper from url-link
    returned = powerpyx_scraper(url)
elif 'psnprofiles' in url and 'guide' in url:
    returned = psnprofiles_scraper(url)
else:  # This scrapes just trophy list
    returned = trophy_scraper(url)



trophy_list = [t.split('\n', maxsplit=1) for t in returned[0]] # Splits by first \n 
trophy_list = [t for t in trophy_list if len(t)>1] # Removes irrelevant lists
trophy_list = [i for i in trophy_list if all(x not in i[0] for x in ['Trophy Guide', 'Collectibles', 'Walkthrough', '100%'])]  # Removes Extra pick ups

game_name = returned[1]
for x in [' Trophy Roadmap', ' Trophy Guide', ' Trophies']:
    game_name = game_name.replace(x, '')

if returned[2] == 2:
    details_list = [d.replace('\n', ' ')[:1500] for d in returned[3]] # Fixes Format



length = len(trophy_list)
data = {}
if returned[2] == 2:
    print(1)
    for i in range(0, length):
        data[i] = {'Trophy': trophy_list[i][0],
                   'Details': trophy_list[i][1],
                   'Notes': details_list[i],
                   'Game': game_name}
elif returned[2] == 1:
    print(2)
    for i in range(0, length):
        data[i] = {'Trophy': trophy_list[i][0],
                   'Details': trophy_list[i][1],
                   'Game': game_name}

tracker_adder(url, DB_ID)



  
