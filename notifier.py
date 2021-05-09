import pytz
import requests
import json
import time
from twilio.rest import Client
from datetime import datetime

#INITs
districtWeekVacanciesURL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"

payload = {}
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}

#Global Variables
session_calls = 0
msgs_sent = 0
last_msg_sent = None

def getWeekVacanciesByDistrict(district_id, date):

    params = {
        'district_id' : district_id,
        'date' : date,
    }

    response = requests.request('GET', districtWeekVacanciesURL, headers=headers, data=payload, params = params)

    if response.status_code == 200:
        return response.text
    elif response.status_code == 400:
        print("Failed to get request. Response: " + str(response.status_code))
        pprint(response.json())
        return None
    else:
        print("Failed to get request. Response: " + str(response.status_code))
        return None

def sendAlert(center_name):
    global msgs_sent
    global last_msg_sent
    
    if(msgs_sent > 20):
        print("Message Limit Reached.")
        return

    if(last_msg_sent is not None):
        diff = last_msg_sent - datetime.now()
        if(diff.total_seconds() < 120):
            print("Message not sent. Last message was within 2 mins.")
            return

    message = "Found Vacancy at: " + str(center_name)

    account_sid = "{twilio_sid}"
    auth_token = "{twilio_auth_token}"
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message,
        from_="{twilio_number}",
        to="{recipient_number}"
    )

    print("Message Sent. Availbility at " + center_name)
    last_msg_sent = datetime.now()
    msgs_sent += 1

if __name__ == '__main__':
    while True:
        try:
            todays_date = datetime.now().strftime("%d-%m-%Y")
            time_now = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%H:%M:%S")
            data = json.loads(getWeekVacanciesByDistrict('365', str(todays_date)))
            
            session_calls += 1
            
            centers18plus = 0
            available = 0
            available_center = ""

            for center in data['centers']:
                for session in center['sessions']:
                    if(session['min_age_limit'] == 18):
                        centers18plus += 1
                        if(session['available_capacity'] > 0):
                            available_center = center['name']
                            available += 1

            if(available > 0):
                sendAlert(available_center)

            print(str(time_now) + " -> Found " + str(centers18plus) + " centers for 18+. " + str(available) + " available.")

            time.sleep(10)

        except KeyboardInterrupt:
            print("\n\nSession Details:")
            print("API Queries: " + str(session_calls))
            print("Messages Sent: " + str(msgs_sent))
            exit(0)