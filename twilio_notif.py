# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 11:37:20 2022

@author: Alice
"""

import json
from twilio.rest import Client

with open('credentials.json', 'r') as f:
    creds = json.load(f)

client = Client(creds["twilio"]["account_sid"], creds["twilio"]["auth_token"])

def send_sms(number, message):
    message = client.messages \
        .create(
            messaging_service_sid='MGc698655e624c15d697502e522479501b',
            body=message,
            to=number
         )

    print(message.sid)
