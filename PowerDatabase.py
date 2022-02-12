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
        self.collection = self.db.rawdata

    def fetch_data(self, data_from):

        data = pd.DataFrame(list(self.collection.find(
            {"timestamp": {"$gt": data_from.timestamp()}}
        )))
        data["timestamp"] = pd.to_datetime(data["timestamp"], unit="s")
        return data

    def get_machine_ids(self):
        machine_ids = list(self.collection.distinct("uid"))
        return machine_ids


class FakePowerDatabase():
    """A fake database for using downloaded data"""

    def __init__(self):
        self.data = pd.read_pickle("data.pk")

    def fetch_data(self, data_from):

        df = self.data[self.data["timestamp"] > data_from.timestamp()]
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        return df

    def get_machine_ids(self):
        machine_ids = list(pd.unique(self.data["uid"]))
        return machine_ids