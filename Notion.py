import requests
API_KEY = "NOTION API"
DB_ID = "DATABASE ID"

headers = {
    "Authorization" : "Bearer " + API_KEY,
    "Content-Type" : "application/json",
    "Notion-Version" : "2022-06-28"} # API Version



def check_game(DB_ID, game_name):  # Adds new game to 'Game' Selections
    url = f'https://api.notion.com/v1/databases/{DB_ID}'
    res = requests.get(url, headers=headers)
    db_info = res.json()
    options = db_info['properties']['Game']['select']['options']
    
    games = [game['name'] for game in options]  # Verifies if game already exists otherwise it adds inserts it in
    if game_name not in games:
        url = 'https://api.notion.com/v1/pages'
        payload = {"parent": {"database_id": DB_ID},
        "properties": {"Game": {"type": "select", "select": {"name": game_name}}}}
        
        res = requests.post(url, json=payload, headers=headers)  



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
    
    for attempt in range(3):  # If it fails to insert allows another go
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            print('Succesful')
            return
        else:
            print('Trying Again')
            sleep(1)



check_game(DB_ID, game_name)
for i in range (0, len(trophy)):
    t, d, n = f'{trophy[i][0]}', f'{trophy[i][1]}', f'{details[i]}'
    
    new_row = {'Trophy':t, 'Details':d, 'Notes':n, 'Game':game_name}
    add_row(DB_ID, new_row)





