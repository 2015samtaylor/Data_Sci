#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sqlalchemy
import pandas as pd

engine = sqlalchemy.create_engine('mysql+pymysql://root:*******@localhost:3306/pollution_db')
engine


# In[ ]:


df = pd.read_csv('bristol-air-quality-updated.csv', sep= ',', dtype = str)
o = df['geo_point_2d']
oo = df['Location']


# In[ ]:


Monitors = pd.concat([oo,o], axis = 'columns') 
Monitors.rename(columns = {'SiteID' : 'Site_ID'}, inplace = True)

Monitors.to_csv('Monitors.csv', index = False)


# In[ ]:


Monitors = pd.read_csv('Monitors.csv')


# In[ ]:


Monitors.to_sql(
    name = 'Monitors',
    con = engine,
    index = False,
    if_exists = 'append'
)


# In[ ]:


df.drop(columns = ['Location', 'geo_point_2d'],inplace = True)
df.drop(df.columns[0], axis = 1, inplace = True)
df.rename(columns = {'Date Time' : 'DateTime'}, inplace = True)


# In[ ]:


df.to_sql(
    name = 'Measurements',
    con = engine,
    index = False,
    chunksize = 1000,
    if_exists = 'append'
)

