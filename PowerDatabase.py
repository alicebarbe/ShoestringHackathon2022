# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 09:22:43 2022

@author: Alice
"""
import pandas as pd
import json
from pymongo import MongoClient
import certifi

class PowerDatabase():

    def __init__(self):
        with open('credentials.json', 'r') as f:
            self.creds = json.load(f)

        self.mongostr = self.creds["mongostr"]
        self.client = MongoClient(self.mongostr, tlsCAFile=certifi.where())

        self.db = self.client["shoestring"]
        self.test_collection = self.db.testdata
        self.raw_collection = self.db.rawdata

    def fetch_data(self, data_from):

        data = pd.DataFrame(list(self.test_collection.find(
            {"timestamp": {"$gt": data_from.timestamp()}}
        )))
        data["timestamp"] = pd.to_datetime(data["timestamp"], unit="s")
        return data