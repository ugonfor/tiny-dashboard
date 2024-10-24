import schedule, time
import datetime

from cvml_manager.datatype import notion_event, credential, google_calendar_event
from cvml_manager.notion_api import get_database_after, get_id2name
from cvml_manager.google_calendar_api import google_auth, get_upcoming_events, get_upcoming_events_minmax

import pandas as pd

from googleapiclient.discovery import build

DATABASE_PATH = 'eventinfo.csv'
ID2NAME_PATH = 'id2name.csv'


global ID2NAME
ID2NAME = pd.read_csv(ID2NAME_PATH).set_index('id').to_dict()['name']
def notion_data_to_database(cred: credential, DATABASE_PATH):

    today = datetime.datetime.now()
    today_before_10 = today - datetime.timedelta(days=10)
    today_before_10 = today_before_10.strftime('%Y-%m-%d')
    events = get_database_after(today_before_10, cred=cred)


    DATABASE = pd.read_csv(DATABASE_PATH, 
                        dtype={'event_id': int, 
                                'title': str, 
                                'time_start': str, 
                                'time_end': str, 
                                'notion_event_id': str,
                                'google_event_id': str})
    
    for event in events:
        exist = False
        if event.id in DATABASE['notion_event_id'].values:
            event_id = DATABASE[DATABASE['notion_event_id'] == event.id]['event_id'].values[0]
            exist = True
            idx = DATABASE[DATABASE['notion_event_id'] == event.id].index[0]
        else:
            # search the event_id in DATABASE
            # and new event_id should be created
            # event_id should be unique and smallest integer number

            event_id = 0
            while event_id in DATABASE['event_id']:
                event_id += 1
        

        people = list(map(lambda x: x['id'], event.people['relation']))
        people = [ID2NAME[person_id][-2:] for person_id in people]
        people = ', '.join(people)
        
        if people != '':
            title = event.title + f' ({people})'
        else:
            title = event.title

        data = {
            'event_id': event_id,
            'title': title,
            'time_start': event.start_time,
            'time_end': event.end_time,
            'notion_event_id': event.id
        }

        if exist:
            data['google_event_id'] = DATABASE.loc[idx, 'google_event_id']
            DATABASE.loc[idx] = data
        else:
            DATABASE = DATABASE._append(data, ignore_index=True)

    erased = []
    for index, row in DATABASE.iterrows():
        if row['notion_event_id'] not in [event.id for event in events]:
            erased.append(index)
    DATABASE = DATABASE.drop(erased)
    
    DATABASE.to_csv(DATABASE_PATH, index=False)

def handle_erased_calendar_events(service, DATABASE_PATH, calendar_id):
    today = datetime.datetime.now()
    today_before_10 = today - datetime.timedelta(days=10)
    today_before_10 = today_before_10.isoformat() + "Z"  # 'Z' indicates UTC time
    today_after_30 = today + datetime.timedelta(days=30)
    today_after_30 = today_after_30.isoformat() + "Z"  # 'Z' indicates UTC time
    events = get_upcoming_events_minmax(service, today_before_10, today_after_30, calendar_id)


    DATABASE = pd.read_csv(DATABASE_PATH, 
                        dtype={'event_id': int, 
                                'title': str, 
                                'time_start': str, 
                                'time_end': str, 
                                'notion_event_id': str,
                                'google_event_id': str})
    
    erased = []
    database_ids = DATABASE['google_event_id'].values
    for event in events:
        if event.id not in database_ids:
            erased.append(event)
    
    for event in erased:
        service.events().delete(calendarId=calendar_id, eventId=event.id).execute()

            
def database_to_calendar(DATABASE_PATH, service, calendar_id):
    DATABASE = pd.read_csv(DATABASE_PATH, 
                        dtype={'event_id': int, 
                                'title': str, 
                                'time_start': str, 
                                'time_end': str, 
                                'notion_event_id': str,
                                'google_event_id': str})
    
    for index, row in DATABASE.iterrows():
        event = {}
        if pd.isnull(row['google_event_id']):

            if 'T' in row['time_end']:
                start_time = datetime.datetime.fromisoformat(row['time_start']).isoformat()
                end_time = datetime.datetime.fromisoformat(row['time_end']).isoformat()

                event['summary'] = row['title']
                event['start'] = {'dateTime': start_time, 'timeZone': 'Asia/Seoul'}
                event['end'] = {'dateTime': end_time, 'timeZone': 'Asia/Seoul'}

            else:
                # end_time + 1
                # since end_day is not included in the event
                end_time = datetime.datetime.strptime(row['time_end'], '%Y-%m-%d')
                end_time += datetime.timedelta(days=1)
                end_time = end_time.strftime('%Y-%m-%d')

                event = {
                    'summary': row['title'],
                    'start': {
                        'date': row['time_start'],
                    },
                    'end': {
                        'date': end_time,
                    },
                }

            try:
                event = service.events().insert(calendarId=calendar_id, body=event).execute()
            except:
                breakpoint()
            DATABASE.at[index, 'google_event_id'] = event['id']
        else:
            event = service.events().get(calendarId=calendar_id, eventId=row['google_event_id']).execute()
            
            # end_time + 1
            # since end_day is not included in the event
            
            if 'T' in row['time_end']:
                start_time = datetime.datetime.fromisoformat(row['time_start']).isoformat()
                end_time = datetime.datetime.fromisoformat(row['time_end']).isoformat()

                event['summary'] = row['title']
                event['start'] = {'dateTime': start_time, 'timeZone': 'Asia/Seoul'}
                event['end'] = {'dateTime': end_time, 'timeZone': 'Asia/Seoul'}
            else:
                start_time = datetime.datetime.strptime(row['time_start'], '%Y-%m-%d').strftime('%Y-%m-%d')
                end_time = datetime.datetime.strptime(row['time_end'], '%Y-%m-%d') # .split("T")[0]
                end_time += datetime.timedelta(days=1)
                end_time = end_time.strftime('%Y-%m-%d')

                
                event['summary'] = row['title']
                event['start']['date'] = start_time
                event['end']['date'] = end_time

            updated_event = service.events().update(calendarId=calendar_id, eventId=row['google_event_id'], body=event).execute()
            DATABASE.at[index, 'google_event_id'] = updated_event['id']


    DATABASE.to_csv(DATABASE_PATH, index=False)

def sync_notion_to_google_calendar(cred: credential, DATABASE_PATH, service):
    notion_data_to_database(cred, DATABASE_PATH)
    database_to_calendar(DATABASE_PATH, service, cred.calendar_id)
    handle_erased_calendar_events(service, DATABASE_PATH, cred.calendar_id)
    
    today = datetime.datetime.now()
    print(f"{today} - Synced")


def main():
    import time
    print(f"Start at {datetime.datetime.now()}")

    # Load credentials
    cred = credential('./keys/secrets.yaml', './keys/credentials.json')
    
    get_id2name(cred, ID2NAME_PATH)

    # Authenticate with Google Calendar API
    service = build("calendar", "v3", credentials=google_auth(cred.OAuth2_path))

    sync_notion_to_google_calendar(cred, DATABASE_PATH, service)

    # # Schedule the sync operation every 5 minutes
    # schedule.every(60).minutes.do(sync_notion_to_google_calendar, cred, DATABASE_PATH, service)
    # # schedule.every(5).seconds.do(sync_notion_to_google_calendar, cred, DATABASE_PATH, service) # for debug
    
    # # Run the scheduler in an infinite loop
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)  # Sleep for 1 second to avoid high CPU usage

if __name__ == "__main__":
    
    # exception handling
    # print error message and traceback
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()