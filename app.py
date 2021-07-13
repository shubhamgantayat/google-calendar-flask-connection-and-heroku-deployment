import os

import flask
from flask import render_template, jsonify, Flask, request
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

app = Flask(__name__)


@app.route('/', methods = ['GET', 'POST'])
def home_page():
    return render_template('form.html')


@app.route('/calendar', methods=['POST'])
def check_prime():
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    if request.method == 'POST':
        string = ''
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES, )
            port = int(os.environ.get('PORT', 5000))
            creds = flow.run_local_server(host='127.0.0.1', port=8080)
            service = build('calendar', 'v3', credentials=creds)

            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            print('Getting the upcoming 10 events')
            events_result = service.events().list(calendarId='addressbook#contacts@group.v.calendar.google.com',
                                                  timeMin=now,
                                                  maxResults=10, singleEvents=True,
                                                  orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                string = 'No upcoming events found.'
            result = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                e = dict(event)
                if 'summary' in e.keys():
                    result.append([start, e['summary']])
            string = result
        except ValueError:
            string = 'Please enter an integer'
        except TypeError:
            string = 'Please enter an integer greater than zero'
        finally:
            return render_template('form.html',results = string)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0',port=port,debug=True)
