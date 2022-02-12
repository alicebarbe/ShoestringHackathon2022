# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 09:22:43 2022

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

# %%
data = pd.DataFrame(list(collection.find()))