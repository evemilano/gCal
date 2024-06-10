import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import time
# Import the library for your specific Pi HAT here

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

def get_upcoming_events(service, minutes_before=2):
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_time = datetime.datetime.fromisoformat(start[:-1])  # remove the 'Z'
        # Check if the event starts within the next two minutes
        if start_time <= datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes_before):
            attendees = event.get('attendees', [])
            confirmed_attendees = [attendee for attendee in attendees if attendee.get('responseStatus') == 'accepted']
            if len(confirmed_attendees) >= 2:
                # This is where you would interact with your Pi HAT to do the signaling
                pass

# Initialize the Google Calendar API service
service = get_calendar_service()

# Main loop
while True:
    get_upcoming_events(service)
    time.sleep(10)  # Check every 10 seconds, you can change this interval
