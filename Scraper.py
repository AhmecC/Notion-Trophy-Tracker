from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep



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

    # Detects Tips & Strategies Section being picked up and allows for removal from details
    a = driver.find_elements(By.CLASS_NAME, 'grow')
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



url = ''
if 'powerpyx' in url: # Auto chooses appropriate scraper
    returned = powerpyx_scraper(url)
elif 'psnprofiles' in url:
    returned = psnprofiles_scraper(url)

trophy_list = [t.split('\n') for t in returned[0]] # Cleans
trophy_list = [t for t in trophy_list if len(t)>1] # Remove irrelevant lists
trophy_list = [i for i in trophy_list if all(x not in i[0] for x in ['Trophy Guide', 'Collectibles'])]  # Remove Extra's

details_list = [d.replace('\n', ' ') for d in returned[1]] # Cleans

game_name = returned[2].replace(' Trophy Roadmap', '')  # Ensures only game name captured
game_name = returned[2].replace(' Trophy Guide', '')

