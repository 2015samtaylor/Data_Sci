#!/usr/bin/env python
# coding: utf-8

# In[22]:


import json
import requests
from gspread_pandas import Spread, Client
import pandas as pd
from urllib.request import urlretrieve as retrieve


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


# function returns access token which is stored in session_output variable. 
session_output = login('team@customplanet.com', 'PRETTY11')

headers_2 = {
    'Authorization': 'Bearer '+session_output
}

# pass in headers, and appropriate URL. Utilize .json method to grab the file. 

URL_2 = 'https://ottocap.com/api/s/download_inventory'
response = requests.get(URL_2, headers=headers_2)
final_url = response.json()['file']



# pass the file into urllib's retrieve method, and declar file as 'ottocap_inventory.csv'
# url = final_url
retrieve(final_url, 'ottocap_inventory.csv')

df = pd.read_csv('ottocap_inventory.csv')
df2 = df[['sku_parent', 'sku_no', 'name', 'color', 'size','instock', 'CA', 'TX', 'GA']].copy()

spread = Spread('Ottocap_Inventory')
spread.df_to_sheet(df2, index = False, sheet = 'Inventory', replace = True, add_filter = True)

