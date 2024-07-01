import requests
import yaml
from pprint import pprint
import datetime

from cvml_manager.datatype import notion_event, credential
import pandas as pd


def get_id2name(cred: credential, output_path) -> dict:
    DATABASE_ID = cred.id2name_DATABASE
    NOTION_API_KEY = cred.NOTION_API_KEY
    
    url = f'https://api.notion.com/v1/databases/{DATABASE_ID}/query'
    headers = {
        'Authorization': 'Bearer ' + NOTION_API_KEY,
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    data = {}

    response = requests.post(url, headers=headers, json=data)
    results = response.json()['results']
    
    
    for result in results:
        print(result['properties']['이름']['title'][0]['plain_text'], result['id'])
        
    df = pd.read_csv(output_path)
    for result in results:
        df = df._append({'id': result['id'], 'name': result['properties']['이름']['title'][0]['plain_text']}, ignore_index=True)
    df.to_csv(output_path, index=False)


def get_database_after(day, cred: credential) -> list[notion_event]:
    
    DATABASE_ID = cred.DATABASE_ID
    NOTION_API_KEY = cred.NOTION_API_KEY
    
    url = f'https://api.notion.com/v1/databases/{DATABASE_ID}/query'
    headers = {
        'Authorization': 'Bearer ' + NOTION_API_KEY,
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    data = {
        "filter": {
            'and':[
                {
                    "property": "날짜",
                    "date": {
                    "on_or_after": day
                    }
                },
                {
                    'or': [
                        {
                            "property": "일정보이기",
                            "checkbox": {
                                "equals": True
                            },
                        },
                        {
                            "property": "디데이표기",
                            "checkbox": {
                                "equals": True
                            },
                        }
                    ]
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=data)
    results = response.json()['results']
    
    results = [notion_event(event) for event in results]
    return results

def main(cred):
    
    today = datetime.datetime.now()
    today_before_10 = today - datetime.timedelta(days=10)
    today_before_10 = today_before_10.strftime('%Y-%m-%d')
    events = get_database_after(today_before_10, cred=cred)
    for event in events:
        print(event)
        # print(event.id)
        print(event.people)
        print(event.raw_data)
    
    get_id2name(cred, './id2name.csv')
    
if __name__ == '__main__':
    cred = credential('./keys/secrets.yaml', './keys/credentials.json')
    main(cred)
    