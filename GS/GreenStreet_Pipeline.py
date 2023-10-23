#!/usr/bin/env python
# coding: utf-8

# In[70]:


# Second run completed for quality, and re-usability 
# Assumption that we want to retain all properties in the data set.

import pandas as pd
from geopy.geocoders import ArcGIS
pd.options.mode.chained_assignment = None
import datetime
import numpy as np
import warnings
warnings.filterwarnings("error", category=FutureWarning)

# read in data from working directory
df = pd.read_csv('data_property.csv')

# --------------------------------------------
# zip, sf, & year built all become floats. This allowed them to appear using df.describe()
# and get a quick snapshot of the data frame.
# Other data types are ok as is. pd.to_numeric also allows me to identfiy NaN values very quickly.

def fix_dtypes():
    
    numeric_cols = ['property_id', 'zip', 'baths', 'beds', 'sf', 'year_built']

    # Declare the proper numeric cols 
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
# ------------------------------------
# The fix location data function is use to acquire the proper address, city, state, & zip. from geopy.geocoders 
# ArcGIS package. The funciton filters for NaN values in zip, and passes in the address, city, state, zip into 
# the geo locator, and it returns raw location data. 


def fix_location_data():

    # Initialize ArcGIS locator
    geolocator = ArcGIS()

    loc_data_list = []
    
    #locate the NaNs within the zip column
    zip_issues = df.loc[df['zip'].isna()]

    # Must have a combination of address and city, or address and zip code. 
    for index, row in zip_issues.iterrows():
        address = row['address']
        city = row['city']
        state = row['state']
        zip_code = row['zip']

        # Concatenate address and city
        location_str = f"{address}, {city}, {state}, {zip_code}"

        # Geocode the location
        location = geolocator.geocode(location_str)

        # Extract the address from the location
        loc_data = location.raw['address']

        loc_data = loc_data.split(',')
        # # Trim leading and trailing spaces from each column
        loc_data = [data.strip() for data in loc_data] 

        #Couple instances where the unit number throws it off on the comma split making the length 5
        if len(loc_data) == 5:
            del loc_data[1]
        else:
            pass
        
        #lastly add in the index, in order to refer to that row for replacement
        loc_data += [index]

        loc_data_list.append(loc_data)
    
    #make a dataframe out of loc_data_list, set the index on idx in order to match up with df and update it
    frame = pd.DataFrame(loc_data_list, columns=['address', 'city', 'state', 'zip', 'idx'])
    frame = frame.set_index('idx')
    
    #turn zip back to numeric d type
    frame['zip'] = pd.to_numeric(frame['zip'], errors='coerce')
    
    df.update(frame)

# ----------------------------------------

# When fixing location data, the ArcGIS package brings back states as a full word instead of acronyms. 
# created a dictionary to map to the proper acronyms as a result

def state_to_abbreviation():

    state_abbreviations = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]

    state_names = [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
        "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
        "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
        "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
        "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
    ]
    
    #zip both lists together in order to create a dictionary to map
    state_dict = dict(zip(state_names, state_abbreviations))
    
    # map the state_dict to the existing column, maintain state value if key is not present
    df['state'] = df['state'].map(state_dict).fillna(df['state'])

# -------------------------------------

# The fill missing sqft function identifies NaN values, and fills them in by 
# calculating the average sf value based on matching state and beds. 
# Assumming that we want to retain all properties in the data set.
# fill_missing_sqft function is below fix_location, and state to abbreviation because the state is a necessity in the filter


def fill_missing_sqft():
    
    #filter frame to loop through using iterows, 100 provides baseline
    sqft_issues = df.loc[(df['sf'].isna()) | (df['sf'] < 100)]

    for index, row in sqft_issues.iterrows():
        state = row['state']
        beds = row['beds']
        
        #state is a necessity here
        frame = df.loc[(df['state'] == state) & (df['beds'] == beds)]

        #if there are not other instances with the beds & state, apply np.nan to aviod in calc but preserve row
        if len(frame) == 1:
            df.loc[df.index == index, 'sf'] = np.nan
        else:
            frame_sqft_val = round(frame['sf'].mean())
            df.loc[df.index == index, 'sf'] = frame_sqft_val
    
# --------------------------------------

# Insert NaN for outliers values based on ratio of beds to sf, and bath to sf. 
# In this way the data is maintained, and numbers can still be calculated.

def alter_faulty_bath_beds():

    df['sf_to_bath'] = round(df['sf'] / df['baths'])
    df['sf_to_beds'] = round(df['sf'] / df['beds'])

    # By identifying values that are less than or equal to 100 it would mean 
    # those are properties that have an odd amount of beds/baths compared to square footage
    # FIltering for NaNs includes values that had NaN for bath or bed making the ratio NaN
    
    df.loc[(df['sf_to_bath'] < 100) | (df['sf_to_bath'].isna()), 'baths'] = np.nan
    df.loc[(df['sf_to_beds'] < 100) | (df['sf_to_beds'].isna()), 'beds'] = np.nan
    
# ------------------------------------------

def alter_year_built():

    #get today as an int
    today_year = datetime.date.today().year
    
    #use the range of 1800-2023 to apply nan vals to extreme outliers 
    df.loc[(df['year_built'] < 1800) | (df['year_built'] > today_year), 'year_built'] = np.nan
        
    # Find vals that are not NaNs. Create the 'years_old' column in that new frame.
    # Create a dictionary based on the index, and apply it back to the original, fill non key vals with NaNs
    df_sub = df.loc[~df['year_built'].isna()]
    df_sub['years_old'] = today_year - df['year_built']
    years_old_dict = df_sub['years_old'].to_dict()
    df['years_old'] = df.index.map(years_old_dict).fillna(np.nan)

# ----------------------------------------

def aggregate_and_display():
    
    # For each state: calculate the minimum square footage, maximum square footage, 
    # and the average age in years of all properties (age = current year - year_built).

    result = df.groupby('state').agg({'sf': ['min', 'max'], 'years_old': 'mean'})
    result['sf'] = result['sf'].astype(int)
    result['years_old'] = result['years_old'].astype(int)

    # reset the index, and drop the multi level index
    result = result.reset_index()
    result.columns = result.columns.droplevel()

    # create a dict to rename the columns accordingly.
    new_cols = ['state', 'sf_min', 'sf_max', 'age_avg']
    new_col_dict = dict(zip(list(result.columns), new_cols))
    result = result.rename(columns = new_col_dict)
    return(result)


fix_dtypes()
fix_location_data()
state_to_abbreviation()
fill_missing_sqft()
alter_faulty_bath_beds()
alter_year_built()
result = aggregate_and_display()


result.to_csv('aggregation_by_state_results.csv', index = False)

# -------------------------------------------------OPTIONAL to detect outliers--------------------------------------------------------

# Use detect outliers function to create a CSV as a form of logging
# Gets the mean and standard deviation 90% percent of the data, and outputs dataframe based on numeric columns
# not falling within that range. 

def detect_outliers():
    
    outliers_list = []

    numeric_cols = ['sf_to_bath', 'sf_to_beds', 'sf', 'year_built', 'years_old']
    
    #iterate through numeric cols to find outliers that are outside of 3.5 standard deviations
    #mean and standard deviation excludes the 5% of mins, and maxes
    for col in numeric_cols:

            frame = pd.DataFrame(df[col].sort_values().reset_index(drop = True))

            # # exclude the extremes at on the mins and max sides when calculating mean and standard deviation. 
            range_1 = round(len(frame.index) * .05)
            range_2 = round(len(frame.index) * .95)
            
            #mean val will not count if column is not numeric. 
            try:
                mean = frame.iloc[range_1:range_2].mean()
                std = frame.iloc[range_1:range_2].std()
            except FutureWarning as warning:
                print(f'Must be a numeric column, not {col}')

            # Calculate the upper and lower bounds with 4 standard deviations. 99% of data should statistically fall within
            upper_bound = round(mean + 3.5 * std)
            lower_bound = round(mean - 3.5 * std)
            
            #find the outliers and add in a column before appending to the outlier frame.
            outliers = df.loc[(df[col] > upper_bound[col]) | (df[col] < lower_bound[col])]
            outliers['outlier_column'] = col
            outliers_list.append(outliers)
        
    #concat brings all frames together. 
    outliers_list = pd.concat(outliers_list)
    return(outliers_list)

    
outliers = detect_outliers()
outliers.to_csv('outliers.csv', index = False)

