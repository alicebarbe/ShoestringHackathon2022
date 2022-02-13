# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 11:37:20 2022

@author: Alice
"""

import json
from twilio.rest import Client
from pymongo import MongoClient
import certifi
import pandas as pd

with open('credentials.json', 'r') as f:
    creds = json.load(f)

# get numbers of users from database
mongostr = creds["mongostr"]
client = MongoClient(mongostr, tlsCAFile=certifi.where())

db = client["shoestring"]
collection = db.notifnumbers
notifnumbers = pd.DataFrame(list(collection.find()))

# send text messages
client = Client(creds["twilio"]["account_sid"], creds["twilio"]["auth_token"])

def send_sms(number, message):
    message = client.messages.create(
        messaging_service_sid='MGc698655e624c15d697502e522479501b',
        body=message,
        to=number)
    print(message.sid)

def send_sms_to_all(message):
    notifnumbers = pd.DataFrame(list(collection.find()))
    for index, row in notifnumbers.iterrows():
        send_sms(row['number'], f"Hi {row['name']}, {message}")
