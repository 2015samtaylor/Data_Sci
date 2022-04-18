#!/usr/bin/env python
# coding: utf-8

# In[32]:


import json
import requests
from gspread_pandas import Spread, Client
import pandas as pd
from urllib.request import urlretrieve as retrieve

class get_otto:
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        
    
    def login(self):
        s = requests.Session()
        payload = {
            'username' : self.username,
            'password' : self.password,
            "grant_type": "password"
        }

        headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic UDcwUTdKZXVBRjBKMHF1UUpKcVh0Vzd3M1NMaVl0MWhKRHVDTFc4OTp4QnE2N21HU2t2V0EyNFR0RUliMDZ0T1FmeVBMZjFySm9lNVBqZlQwek5EZXNlbWtZSjdJek9taFVlVHFpUGNTUEU0RFlpTERQNjdIQ3NnWnJNSjlTYkZ4R2h4T1AwQm1KYUl4QnZUYjF4REpJZHFOejExSzFxUlZwU2pHM21ndQ=='
        }

        res = s.post('https://ottocap.com/signin/token/', headers=headers, data=payload)

        session_output = (json.loads(res.content)['access_token'])
        
        headers_2 = {
        'Authorization': 'Bearer '+session_output
        }
        
        URL_2 = 'https://ottocap.com/api/s/download_inventory'
        response = requests.get(URL_2, headers=headers_2)
        final_url = response.json()['file']
        
        return(final_url)
        
    
# passing in variables to create object, final output returns unique url with AWS access key id
# url is passed into function to create dataframe. Frame is sent to Google Sheets. 

otto_calls = get_otto('team@customplanet.com', 'PRETTY11')

def retrieve_send():

    retrieve(otto_calls.login(), 'ottocap_inventory.csv')
    
    df = pd.read_csv('ottocap_inventory.csv')
    df2 = df[['sku_parent', 'sku_no', 'name', 'color', 'size','instock', 'CA', 'TX', 'GA']].copy()

    spread = Spread('Ottocap_Inventory')
    spread.df_to_sheet(df2, index = False, sheet = 'Inventory', replace = True, add_filter = True)

