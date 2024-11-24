from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']


def authenticate_google():
    """Authenticates and returns Google Calendar API service."""
    creds = None
    # Token file stores the user's credentials after the first authentication
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If credentials are invalid or do not exist, prompt the user to authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)


def create_google_meet_event(service, event_details):
    """Creates a Google Calendar event with a Meet link."""
    event = {
        'summary': event_details['summary'],
        'start': {
            'dateTime': event_details['start_time'],  # ISO 8601 format
            'timeZone': 'UTC',  # Adjust as needed
        },
        'end': {
            'dateTime': event_details['end_time'],  # ISO 8601 format
            'timeZone': 'UTC',  # Adjust as needed
        },
        'attendees': [{'email': email} for email in event_details.get('attendees', [])],
        'conferenceData': {
            'createRequest': {
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                'requestId': 'some-random-string',
            },
        },
    }
    event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()

    print(f"Event created: {event.get('htmlLink')}")
    print(f"Google Meet link: {event['conferenceData']['entryPoints'][0]['uri']}")


def main():
    service = authenticate_google()

    # Get event details from user input
    summary = input("Enter event summary: ")
    start_time_input = input("Enter event start time (YYYY-MM-DD HH:MM:SS): ")
    end_time_input = input("Enter event end time (YYYY-MM-DD HH:MM:SS): ")
    attendees = input(
        "Enter attendee emails separated by commas (optional): ").split(',')

    # Convert start_time and end_time to ISO 8601 format
    start_time = datetime.strptime(start_time_input, "%Y-%m-%d %H:%M:%S").isoformat()
    end_time = datetime.strptime(end_time_input, "%Y-%m-%d %H:%M:%S").isoformat()

    # Create event details dictionary
    event_details = {
        'summary': summary,
        'start_time': start_time,
        'end_time': end_time,
        'attendees': [email.strip() for email in attendees if email.strip()],
    }

    # Create the event
    create_google_meet_event(service, event_details)


if __name__ == '__main__':
    main()
