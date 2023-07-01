#!/usr/bin/env python
# coding: utf-8

# In[1]:


# First iteration assumption completed for timing purposes roughly 30-40 min

import datetime
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None


# read in the data frame from working directory
df = pd.read_csv('data_property.csv')


# create a funciton to make the continuous variable columns as numeric type
def fix_dtypes():
    
    numeric_cols = ['property_id', 'zip', 'baths', 'beds', 'sf', 'year_built']

    # Declare the proper numeric cols 
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')


def create_columns():
    # create ratios for square feet of bath & bed in order to find outliers
    df['sf_to_bath'] = round(df['sf'] / df['baths'])
    df['sf_to_beds'] = round(df['sf'] / df['beds'])

    # create today_year in order to use for 'years_old' column
    today_year = datetime.date.today().year

    # Find vals that are not NaNs. Create the 'years_old' column in that new frame.
    # Create a dictionary based on the index, and apply it back to the original, fill non key vals with NaNs
    df_sub = df.loc[~df['year_built'].isna()]
    df_sub['years_old'] = today_year - df['year_built']
    years_old_dict = df_sub['years_old'].to_dict()
    df['years_old'] = df.index.map(years_old_dict).fillna(np.nan)
    
        
# create a function to detect outliers outside of 3 standard deviations, and utilize the created outlier column
# to find the outliers with relative speed. 

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
            
            mean = frame.iloc[range_1:range_2].mean()
            std = frame.iloc[range_1:range_2].std()
   
            # Calculate the upper and lower bounds with 4 standard deviations. 99% of data should statistically fall within
            upper_bound = round(mean + 3.5 * std)
            lower_bound = round(mean - 3.5 * std)
            
            # in the case of this the lower bound become negative, have it default to zero for filtering purposes
            if lower_bound[col] < 0:
                lower_bound[col] = 0
            
            #find the outliers and add in a column before appending to the outlier frame.
            outliers = df.loc[(df[col] > upper_bound[col]) | (df[col] < lower_bound[col])]
            outliers['outlier_column'] = col
            outliers_list.append(outliers)
        
    #concat brings all frames together. 
    outliers_list = pd.concat(outliers_list)
    return(outliers_list)


def drop_rows():
    # eyeball the rows in the outliers frame, and drop them for timing purposes
    rows_to_drop = [587, 227, 407, 479, 407, 515]
    # Drop outlier rows with specific indexes
    df.drop(index=rows_to_drop, inplace=True)


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
create_columns()
outliers = detect_outliers()
drop_rows()
result = aggregate_and_display()


# Write results to a csv
result.to_csv('aggregation_by_state_results.csv', index = False)


# --------scratch code---

# constantly used df.describe() to see the extremes and make corrections here
# This code below also be used for the quick unique values in lower length columns

# for cols in list(df.columns):
#     print('\n' + cols)
#     print(df[cols].unique()[:30])

