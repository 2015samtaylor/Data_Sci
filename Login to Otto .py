#!/usr/bin/env python
# coding: utf-8

# In[77]:


import json
import requests
from gspread_pandas import Spread, Client


def login(mail, password):
    s = requests.Session()
    payload = {
        'username' : mail,
        'password' : password,
        "grant_type": "password"
    }
    
    headers={
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic UDcwUTdKZXVBRjBKMHF1UUpKcVh0Vzd3M1NMaVl0MWhKRHVDTFc4OTp4QnE2N21HU2t2V0EyNFR0RUliMDZ0T1FmeVBMZjFySm9lNVBqZlQwek5EZXNlbWtZSjdJek9taFVlVHFpUGNTUEU0RFlpTERQNjdIQ3NnWnJNSjlTYkZ4R2h4T1AwQm1KYUl4QnZUYjF4REpJZHFOejExSzFxUlZwU2pHM21ndQ=='
    }
    
    res = s.post('https://ottocap.com/signin/token/', headers=headers, data=payload)
        
    return(json.loads(res.content)['access_token'])

session_output = login('team@customplanet.com', 'PRETTY11')

headers_2 = {
    'Authorization': 'Bearer '+session_output
}

response = requests.get(URL_2, headers=headers_2)

final_url = response.json()['file']

import pandas as pd
from urllib.request import urlretrieve as retrieve

url = final_url
retrieve(url, 'ottocap_inventory.csv')

df = pd.read_csv('ottocap_inventory.csv')

spread = Spread('Ottocap_Inventory')
spread.df_to_sheet(df, index = False, sheet = 'Inventory', replace = True)

