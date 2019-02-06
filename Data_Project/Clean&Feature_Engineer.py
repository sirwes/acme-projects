import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import csv
import os
import sys

#Cleaning
# open .tar.gz files in gitbash: tar xvzf __filename__.tar.gz
# Folder names: 'csvFiles' (for Arizona), 'NevadaCSVs' (for Nevada), 'COCSVs' (for Colorado), 'NMCSVs' (for New Mexico)
'''
Arizona Totals: 10796 data points
Nevada Totals: 965 data points
Colorado Totals: 12499 data points
California Totals: 26745 data points
TOTAL DATA: 51005 points (AFTER CLEANING)
'''

AZ_cities = []
CO_cities = []
NV_cities = []
CA_cities = []

AZpath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname('AZCSVs')))
COpath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname('COCSVs')))
NVpath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname('NVCSVs')))
CApath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname('CACSVs')))

for file1 in os.listdir(str(AZpath)+'/AZCSVs'):
    AZ_cities.append(file1)
for file2 in os.listdir(str(COpath)+'/COCSVs'):
    CO_cities.append(file2)
for file3 in os.listdir(str(NVpath)+'/NVCSVs'):
    NV_cities.append(file3)
for file4 in os.listdir(str(NVpath)+'/CACSVs'):
    CA_cities.append(file4)
    
AZ_cities.sort()
CO_cities.sort()
NV_cities.sort()
CA_cities.sort()

AZdata = []
COdata = []
NVdata = []
CAdata = []

for i in AZ_cities:
    with open(str(AZpath)+'/AZCSVs/'+i) as infile:
        lines = csv.reader(infile)
        for line in lines:
            AZdata.append(line)

for i in CO_cities:
    with open(str(COpath)+'/COCSVs/'+i) as infile:
        lines = csv.reader(infile)
        for line in lines:
            COdata.append(line)
            
for i in NV_cities:
    with open(str(NVpath)+'/NVCSVs/'+i) as infile:
        lines = csv.reader(infile)
        for line in lines:
            NVdata.append(line)
            
for i in CA_cities:
    with open(str(NVpath)+'/CACSVs/'+i) as infile:
        lines = csv.reader(infile)
        for line in lines:
            CAdata.append(line)
            
AZdf = pd.DataFrame(AZdata)
COdf = pd.DataFrame(COdata)
NVdf = pd.DataFrame(NVdata)
CAdf = pd.DataFrame(CAdata)

            
df = AZdf.append(COdf.append(NVdf.append(CAdf)))
df = df.drop(0,axis=1)
df = df.rename(index=str, columns={1:'Bedrooms',
                                   2:'Bathrooms',
                                   3:'HouseSize(sqft)',
                                   4:'LotSize(acre)',
                                   5:'YearBuilt',
                                   6:'City',
                                   7:'State',
                                   8:'Zipcode',
                                   9:'Stories',
                                   10:'SoldPrice',
                                   11:'Foreclosed',
                                   12:'DateSold',
                                   13:'DatePosted',
                                   14:'WalkScore',
                                   15:'InternetSpeed',
                                   16:'UtilityCosts',
                                   17:'InitialPrice',
                                   18:'ElementarySchoolRating',
                                   19:'MiddleSchoolRating',
                                   20:'HighSchoolRating'})


bed = df.loc[df['Bedrooms'] == "Beds"] # contains all rows where their data is just the column names

df = df.drop([i for i in bed.index]) # gets rid of all rows that are the column names. This happened because
                                     # we had lots of different files (~300) with the column names at the top,
                                     # which was recognized by our script as a new row of data and not a 
                                     # continuation of the column titles (682 data points).

df = df.dropna(how='all')
df = df.drop(['InitialPrice'], axis=1) # missing 39802 data points
df = df.drop(['WalkScore'], axis=1)  # data is corrupt

df = df.drop(['InternetSpeed'],axis=1) # missing 2067 data points (and unnecessary)
df = df.drop(['MiddleSchoolRating'], axis=1) # missing 6514 data points
df = df.drop(['HighSchoolRating'], axis=1) # missing 13450 data points, so we're taking it out

# 1 acre == 43560 sqft
sqftConverter = 43560
for index, row in df.iterrows():
    if str(row['LotSize(acre)']).find('sqft') != -1: # checks if it is in sqft or acres
        x = [int(s) for s in re.findall(r'\b\d+\b', row['LotSize(acre)'])] # pulls the digits out of the string
        num = round(int(''.join(map(str,x)))/sqftConverter,3) # concotenate the numbers into 1 (if it has commas)
        newval = str(num) # converts to acres
        row['LotSize(acre)'] = float(newval) # new value is set 
        
    elif str(row['LotSize(acre)']).find('/') != -1: # fractions
        x = [s for s in re.findall(r'(\d.*) acre', row['LotSize(acre)'])][0]  # pulls the digits out of the string
        if len(x) == 3: # less than 1 (just the fraction)
            num = ''.join(map(str,x))
            num = round(int(num[0])/int(x[-1]),3)
            newval = str(num)
            row['LotSize(acre)'] = float(newval)
        elif len(x) > 3: # greater than 1 (mixed fraction)
            x2 = [s for s in re.findall(r'\b\d+\b', x[:-3])]
            num = ''.join(map(str,x2))
            num = int(x2) + round(int(x[-3])/int(x[-1]),3)
            newval = str(num)
            row['LotSize(acre)'] = float(newval)
            
    elif str(row['LotSize(acre)']).find('.') != -1: # decimals
        x = [s for s in re.findall(r'(\d.*) acre', row['LotSize(acre)'])] # pulls the digits out of the string
        num = round(int(''.join(map(str,x))))
        num = round(float(num),3)
        newval = str(num)
        row['LotSize(acre)'] = float(newval)
        
    elif str(row['LotSize(acre)']).find('~') != -1: # integer estimate
        x = [s for s in re.findall(r'~(.*) acre', row['LotSize(acre)'])]  # pulls the digits out of the string
        num = round(int(''.join(map(str,x))))
        num = round(float(num),3)
        newval = str(num)
        row['LotSize(acre)'] = float(newval)

stringsBedrooms = df.loc[df['Bedrooms'].str.contains('scraping')]
df = df.drop([i for i in stringsBedrooms.index])

for index,row in df.iterrows():
    if row['Zipcode'] is None:
        row['Zipcode'] = np.nan

zips = df.Zipcode.unique()
notZips = []
areZips = []
for i in zips:
    try:
        if not i.isdigit():
            notZips.append(i)
        else:
            areZips.append(i)
    except:
        print(i)
        continue
'''
Cleans up data where the zip code has a county name in it instead of a zip code
A total of 98 data points were cleaned from this.

Initial data points: 37949
Ending data points: 37851
'''
for index, row in df.iterrows():
    try:
        if not row.Zipcode.isdigit():
            df = df.drop(index)
    except:
        continue

indexes2Delete = []
for index, row in df.iterrows():
    try:
        # if the sold price value in the row has a '$'
        if row['SoldPrice'].find('$') != -1:
            row['SoldPrice'] = float(re.sub(',','',row['SoldPrice'][1:]))/1e6
        else:
            row['SoldPrice'] = float(re.sub(',','',row['SoldPrice']))/1e6
        # check if HouseSize has a comma
        if row['HouseSize(sqft)'].find(',') != -1:
            # if it does, take it out and make a float out of the digits
            row['HouseSize(sqft)'] = float(re.sub(',','',row['HouseSize(sqft)']))
        # if it's empty, turn it into NAN
        elif row['HouseSize(sqft)'] == '':
            row['HouseSize(sqft)'] = np.nan
        # if Utility Costs is not empty
        if row.UtilityCosts != '':
        # run regex to regrab everything in row
            row['UtilityCosts'] = float(re.compile('\$(.*) \/mo').findall(row['UtilityCosts'])[0])
        else:
            row['UtilityCosts'] = np.nan
            
    except ValueError as e:
        indexes2Delete.append(index)
# delete bad crap
df = df.drop(indexes2Delete)
df = df.reset_index(drop=True)

# replace all empty values with NaN
df.replace("",np.nan,inplace=True)
# replace all '-' values (only occurs in bedrooms) with 1, which seems fair since every house has at least 1
df.replace("–",'1',inplace=True)
# replace some extraneously placed string values with correct ones
df.Stories.replace('5+','5',inplace=True)
# convert values in 'Bathrooms' feature to float
df.Bathrooms = df.Bathrooms.astype(float)
# convert values in 'Bedrooms' feature to float
df.Bedrooms = df.Bedrooms.astype(float)
# convert values in 'YearBuilt' feature to float
df.YearBuilt = df.YearBuilt.astype(float)
# convert values in 'Stories' feature to float
df.Stories = df.Stories.astype(float)
# convert values in 'ElementarySchoolRating' feature to float
df.ElementarySchoolRating = df.ElementarySchoolRating.astype(float)
# removed rows containing NaN values in feature 'YearBuilt'
df=df.dropna(subset=['YearBuilt'])
# removed rows containing NaN values in feature 'ElementarySchoolRating'
df=df.dropna(subset=['ElementarySchoolRating'])

# create mask to find all NaN values in feature 'UtilityCosts'
maskUtil= df.UtilityCosts.isna()
# find average value of all Utility costs
UtilAvg = np.average(df.UtilityCosts[~maskUtil])
# replace all NaN values with the average Utility costs
df.UtilityCosts.replace(np.nan,UtilAvg,inplace=True)
# Lot size is the last feature with NaNs
df = df.dropna(how='any')


#Feature Engineering


# Average days on market for houses in AZ,NV,CO,CA
AZAvg = 83
NVAvg = 84
COAvg = 79
CAAvg = 75.5
badDates = []
# initialize new column for feature to say how long the house was on the market
df['DaysOnMarket'] = 0
dom = []
for index,row in df.iterrows():
    #converts date strings to dates
    datePostedDT = pd.to_datetime(row.DatePosted)
    dateSoldDT = pd.to_datetime(row.DateSold)
    # finds time difference between the DatePosted and DateSold features
    daysOnMarket = (dateSoldDT - datePostedDT).days
    # if date sold is BEFORE date posted, replace values with the state
    # averages for days on market.
    if daysOnMarket < 0:
        if row.State == 'AZ':
            dom.append(AZAvg)
        elif row.State == 'CO':
            dom.append(COAvg)
        elif row.State == 'NV':
            dom.append(NVAvg)
        elif row.State == 'CA':
            dom.append(CAAvg)
        else:
            badDates.append(index)
    # if the value is NaN, replace with state averages as well
    elif daysOnMarket is np.nan:
        if row.State == 'AZ':
            dom.append(AZAvg)
        elif row.State == 'CO':
            dom.append(COAvg)
        elif row.State == 'NV':
            dom.append(NVAvg)
        elif row.State == 'CA':
            dom.append(CAAvg)
    else:
        # appends days on market values to list
        dom.append(daysOnMarket)
    row.DatePosted = datePostedDT
    row.DateSold = dateSoldDT
# initialize DataFrame column to new values
df['DaysOnMarket'] = dom

# save data to new file before 1-hot encoding
with open('DataForVisualization.csv', 'w') as writeFile:
    df.to_csv(writeFile, sep='\t',encoding='utf-8', index=False)

#one-hot encode certain features
df = pd.get_dummies(df,drop_first=True,columns=['Foreclosed'])
df = pd.get_dummies(df,drop_first=True,columns=['State'])

with open('RealEstateData.csv', 'w') as writeFile:
    df.to_csv(writeFile, sep='\t',encoding='utf-8', index=False) 
# written to .csv file without index numbers
