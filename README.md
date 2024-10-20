# notion2google-calendar

## file info

```
credentials.json: OAuth2 credentials file from google OAuth2
secrets.yaml: NotionAPI Key and database ID
eventinfo.csv: calendar event database csv file
```

secrets.yaml은 직접 채워줘야하고, 나머지는 알아서 생성됨.
```
NOTION_API_KEY: <https://www.notion.so/profile/integrations 에서 API KEY 붙여넣기>
DATABASE_ID: <calendar database의 id 붙여넣기. copy link하고나서 ?앞에 나오는 값이 database_id임.>
calendar_id: <google calendar의 cvml calendar 설정 들어가서, 캘린더 ID로 나오는 것임.>
id2name_DATABASE: <인사관리 database의 id 붙여넣기. copy link하고나서 ?앞에 나오는 값이 database_id임.>
```
## How to use:

```
crontab -e
```

```
0 * * * * cd /path/to/notion2google-calendar && python main.py > log.txt
```
