import yaml

class credential:
    def __init__(self, secrets_path, OAuth2_path):
        secrets = yaml.load(open(secrets_path), yaml.FullLoader)
                
        self.DATABASE_ID = secrets['DATABASE_ID']
        self.NOTION_API_KEY = secrets['NOTION_API_KEY']
        self.OAuth2_path = OAuth2_path
        self.calendar_id = secrets['calendar_id']
        self.id2name_DATABASE = secrets['id2name_DATABASE']

class notion_event:
    def __init__(self, event):
        
        try:
            self.id = event['id']
            self.title = event['properties']['Name']['title'][0]['plain_text']
            self.start_time = event['properties']['날짜']['date']['start']
            
            self.end_time = event['properties']['날짜']['date']['end'] 
            if self.end_time is None:
                self.end_time = self.start_time
                
            self.people = event['properties']['담당자']
        except:
            print(f'excpetion occured at {event}')
        self.raw_data = event
    
    def __str__(self):
        return f'{self.title} ({self.start_time} ~ {self.end_time})'
    
    
class google_calendar_event:
    def __init__(self, event):
        self.id = event['id']
        self.title = event['summary']
        self.start_time = event['start'].get('dateTime', event['start'].get('date'))
        
        self.end_time = event['end'].get('dateTime', event['end'].get('date'))
        if self.end_time is None:
            self.end_time = self.start_time
        
        self.raw_data = event
    
    def __str__(self):
        return f'{self.title} ({self.start_time} ~ {self.end_time})'
    
    def __repr__(self):
        return f'{self.title} ({self.start_time} ~ {self.end_time})'
    
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)