import os

import flask
from flask import render_template, jsonify, Flask, request
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

app = Flask(__name__)


@app.route('/', methods = ['GET', 'POST'])
def home_page():
    return render_template('form.html')


@app.route('/calendar')
def calendar():
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    string = ''
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES, redirect_uri=flask.url_for('calendar',_external=True))
    if 'code' not in flask.request.args:
        auth_uri,_ = flow.authorization_url()
        print(auth_uri)
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='addressbook#contacts@group.v.calendar.google.com',
                                              timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        result = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            e = dict(event)
            if 'summary' in e.keys():
                result.append(' - '.join([start, e['summary']]))
        string = ', '.join(result) if len(result) != 0 else 'No birthdays found on your google calendar'
        return render_template('form.html',results = string)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0',port=port,debug=True)
