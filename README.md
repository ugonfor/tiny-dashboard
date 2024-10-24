# notion2google-calendar

## file info

keys 폴더 아래에 다음 두 파일을 생성해주어야함.
```
credentials.json: OAuth2 credentials file from google OAuth2
secrets.yaml: NotionAPI Key and database ID
```

secrets.yaml은 아래 내용 복붙해서, 필요한 부분을 채워줘야함.
```
NOTION_API_KEY: <https://www.notion.so/profile/integrations 에서 API KEY 붙여넣기>
DATABASE_ID: <calendar database의 id 붙여넣기. copy link하고나서 ?앞에 나오는 값이 database_id임.>
calendar_id: <google calendar의 cvml calendar 설정 들어가서, 캘린더 ID로 나오는 것임.>
id2name_DATABASE: <인사관리 database의 id 붙여넣기. copy link하고나서 ?앞에 나오는 값이 database_id임.>
```

credentials.json은 google cloud api에서 OAuth 인증 키를 붙여넣어주어야함.

아래처럼, 1) 프로젝트 하나 만들고 2) OAuth2 사용자 하나 만들고 3) 클라우드 키 다운받기. 
그다음 다운 받은 파일을 credentials.json으로 바꿔서 keys 폴더 아래에 넣어주세요.
![image](https://github.com/user-attachments/assets/2ea6dfa2-8f82-4f02-a370-0cb4e43ed75b)


## How to use:

```
crontab -e
```

```
0 * * * * cd /path/to/notion2google-calendar && python main.py > log.txt
```
