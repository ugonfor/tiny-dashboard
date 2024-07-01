import datetime
import os.path

from cvml_manager.datatype import google_calendar_event

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def google_auth(credentials_path="./keys/credentials.json", token_path="./keys/token.json"):
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(token_path):
      creds = Credentials.from_authorized_user_file(token_path, SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
      else:
          flow = InstalledAppFlow.from_client_secrets_file(
              credentials_path, SCOPES
          )
          creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open(token_path, "w") as token:
          token.write(creds.to_json())
  return creds

def get_upcoming_events(service, timemin, calendar_id):
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  # Call the Calendar API

  events_result = (
      service.events()
      .list(
          calendarId=calendar_id,
          timeMin=timemin,
          singleEvents=True,
          orderBy="startTime",
      )
      .execute()
  )
  events = events_result.get("items", [])

  if not events:
    print("No upcoming events found.")
    return

  events = list(map(google_calendar_event, events))
  return events

def get_upcoming_events_minmax(service, timemin, timemax, calendar_id):
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  # Call the Calendar API

  events_result = (
      service.events()
      .list(
          calendarId=calendar_id,
          timeMin=timemin,
          timeMax=timemax,
          singleEvents=True,
          orderBy="startTime",
      )
      .execute()
  )
  events = events_result.get("items", [])

  if not events:
    print("No upcoming events found.")
    return

  events = list(map(google_calendar_event, events))
  return events

def main():
  creds = google_auth('./keys/credentials.json')

  service = build("calendar", "v3", credentials=creds)
  time = datetime.datetime.now().isoformat() + "Z"  # 'Z' indicates UTC time
  try:
    get_upcoming_events(service,time, 'primary')

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()