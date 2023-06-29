#!/usr/bin/env python
# coding: utf-8

# In[47]:


# Create DB, Create Collection, & Insert Many Documents

import pprint
import json
import pandas as pd
import pymongo
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')

# Neither of these existed, but both were created, first the production DB, and then the person_collection
# To clear out the table
production.person_collection.drop() 
client = MongoClient('mongodb://localhost:27017/')
production = client.production
person_collection = production.person_collection

# -----------------------------------------------------------------------Creating Data

def create_documents():
    first_names = ['Tim', 'Sarah', 'Jennifer', 'Jose', 'Brad', 'Allen']
    last_names = ['Ruscica', 'Smith', 'Bart', 'Cater', 'Pit', 'Geral']
    ages = [21, 40, 23, 19, 35, 67]
    
    docs = []
    
    for first_name, last_name, age in zip(first_names, last_names, ages):
        doc = {'first_name' : first_name, 'last_name': last_name, 'age': age}
        docs.append(doc)
    
    #call on newly created DB
    person_collection.insert_many(docs)
        
    
create_documents()

# ---------------------------------------------------------------------------

# SQL Equivalent

# CREATE TABLE person(
#     _id INT NOT NULL,
#     first_name VARCHAR(100),
#     last_name VARCHAR(100),
#     age INT,
#     PRIMARY KEY (_id)
# );

# INSERT INTO person(
#     first_name,
#     last_name,
#     age
# ) VALUES (
#     'Tim',
#     'Ruscica',
#     21
# )
    
# --------------------------------------------------------------FINDING DATA

def find_all_people():

    people = person_collection.find({})

    for person in people:
        pprint.pprint(person)
        
# ----------------------------------------------------------------

def find_last_name():
    
    cater = person_collection.find_one({'last_name': 'Cater'})
    printer.pprint(cater)
    
# --------------------------------------------------------
    
def count_all_people():
    print(person_collection.count_documents(filter={'last_name': 'Cater'}))   #filter allows you to count mroe specific
    
# SQL Equivalent
#SELECT COUNT(*) FROM person

# --------------------------------------------------------

def get_person_by_id(person_id):

    person = person_collection.find_one({'_id': ObjectId(person_id)})
    pprint.pprint(person)
    
get_person_by_id('649a48fe427b075ec6e0e6e0')

# SQL Equivalent
#SELECT * FROM person WHERE id = person_id

# --------------------------------------------------------
def get_age_range(min_age, max_age):
    query = {
            'age': {
                '$gte': 10,
                '$lte': 20
            }
        }

    people = person_collection.find(query).sort('age')
    for person in people:
        pprint.pprint(person)
        
# p = get_age_range(10, 35)

# SQL Equivalent 

# SELECT * FROM people
# WHERE age >= 10 AND age <= 20
# ORDER BY age;

# ---------------------------------------------------------

def project_columns():
    columns = {'_id': 0,
              'first_name': 1,
              'last_name': 1}
    
    people = person_collection.find({}, columns)
    for person in people:
        pprint.pprint(person)
        

# SQL Equivalent

# SELECT first_name, last_name
# FROM people;

# ----------------------------------------------------------UPDATES
def update_person_by_id(person_id):
    _id = ObjectId(person_id)
    
    all_updates = {
        '$set': {'new_field': True},
        '$inc': {'age': 1},
        '$rename': {'first_name': 'first', 'last_name': 'last'}
    }
    person_collection.update_one({'_id': _id}, all_updates)
    
    #unset the 'new_field created'
    #person_collection.update_one({'_id': _id}, {'$unset': {'new_field': ''}})
    
update_person_by_id('649a4dcc427b075ec6e0e6ec')

# SQL Equivalent

# UPDATE person_collection
# SET new_field = True
# WHERE id = 'person_id';

# UPDATE person_collection
# SET age = age + 1
# WHERE id = 'person_id';

# ALTER TABLE person_collection
# RENAME COLUMN first_name TO first, last_name TO last;

# --------------------------------------------------------

def replace_one(person_id):
    _id = ObjectId(person_id)
    
    new_doc = {
        'first_name': 'new first name',
        'last_name': 'new last name',
        'age': 100
    }
    
    person_collection.replace_one({'_id': _id}, new_doc)
    
replace_one('649a51ec427b075ec6e0e6f4')

# SQL equivalent

# UPDATE person_collection
# SET first_name = 'new first name', last_name = 'new last name', age = 100
# WHERE id = '649a51ec427b075ec6e0e6f4';


# ---------------------------------------------Relationships/ Add Embdedded Address

address = {
    '_id': '62475964011a9126a4cebeb7',
    'street': 'Bay Street',
    'number': 2706,
    'city': 'San Francisco',
    'country': 'United States',
    'zip': '94107',
    'owner_id': '62475964011a9126a4'
}

person  = {
    '_id': '62475964011a9126a4',
    'first_name': 'John'
    
}

# document embeds is necessary here to combine the two above. This is more efficient then storing in two seperate documents.
# If we did want to store them in different collections, we can still maintain the relationship through a foreign key.
# In this case owner_id is the foreign ID in order to create joins. 


person  = {
    '_id': '62475964011a9126a4',
    'first_name': 'John',
    'address' : {
        '_id': '62475964011a9126a4cebeb7',
        'street': 'Bay Street',
        'number': 2706,
        'city': 'San Francisco',
        'country': 'United States',
        'zip': '94107'
    }
    
    
}


def add_address_embed(person_id, address):
    
    _id = ObjectId(person_id)
    
    #add an array of addresses
    #Add the address to the key addresses, set indicates an array. 
    
    #If it does not exist, it will be created, otherwise created
    
    
    person_collection.update_one({'_id': _id}, {'$addToSet': {'addresses': address}})
    
add_address_embed('649df01c427b075ec6e0e6fd', address)

# SQL equivalent

# UPDATE person_collection
# SET addresses = array_append(addresses, 'address')
# WHERE id = '649df01c427b075ec6e0e6fd';

# ---------------------------------------------------------

# Method 2, create a new collection, and reference the address from person_collection as a foreign_key being the 
# person ID from the person_collection collection

def add_address_relationship(person_id, address):
    
    _id = ObjectId(person_id)
    
    #do not want to mutate the array, and add owner_id to the address
    address = address.copy()
    address['owner_id']= person_id
    
    #create a new collection & insert a document
    address_collection = production.address
    address_collection.insert_one(address)
    
    
add_address_relationship('649df01c427b075ec6e0e6fc', address)

# SQL Equivalent

# INSERT INTO address_table (address, owner_id)
# VALUES ('address', '649df01c427b075ec6e0e6fc');

