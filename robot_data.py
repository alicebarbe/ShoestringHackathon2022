# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 07:25:19 2022

@author: Alice
"""

import pandas as pd
import plotly.graph_objects as go
import json
from pymongo import MongoClient
import certifi


with open('credentials.json', 'r') as f:
    creds = json.load(f)

mongostr = creds["mongostr"]
client = MongoClient(mongostr, tlsCAFile=certifi.where())

db = client["shoestring"]
collection = db.testdata

# %% Process example file

df = pd.read_csv('robot.txt', index_col=False, delimiter=" ", names=['time', 'space', 'current', 'uid'])
df = df[['time', 'current', 'uid']]
df['time'] = pd.to_datetime(df['time'])
df['timestamp'] = df['time'].apply(lambda x: x.timestamp())

df_grouped = df.groupby(pd.Grouper(key='time',freq='1min')).mean().reset_index()
df_grouped['uid'] = df['uid'][0]
df_upload = df_grouped[['timestamp', 'current', 'uid']]

# %%
collection.insert_many(df.to_dict('records'))