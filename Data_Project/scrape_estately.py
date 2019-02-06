import os
from selenium import webdriver
import pandas as pd
import re
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys
import numpy as np
import time

columnList = ['Beds',
              'Baths',
              'HouseSize',
              'LotSize',
              'YearBuilt',
              'City',
              'State',
              'Zipcode',
              'InteriorLevels',
              'SoldPrice',
              'Foreclosed',
              'DateSold',
              'DatePosted',
              'Walkscore',
              'InternetSpeed',
              'UtilityCosts',
              'InitialPrice',
              'ElementarySchoolRating',
              'MiddleSchoolRating',
              'HighSchoolRating']
stateURLs2Scrape = ['https://www.estately.com/recently-sold/CA',
                    'https://www.estately.com/recently-sold/CO',	
                    'https://www.estately.com/recently-sold/AZ',	
                    'https://www.estately.com/recently-sold/NV']

def regexFind(reText,line,first=True):
    """finds text in the given line"""
    finder = re.compile(reText)
    locatedText = finder.findall(line)
    if len(locatedText) == 0:
        locatedText = np.nan   #if we couldn't find anything, return nan
    else:
        if first:
            locatedText = locatedText[0]
    return locatedText
    
def ParseListingDeets(listingDeets):
    """
    Uses RegEx to parse through the listing details 
    It looks like this:
         '5 beds 3 baths 1,841 sqft 8,057 sqft lot $23 per sqft 1972 build 115 days on site'
    returns a list of the info
    """
    beds = regexFind('(.+?) bed',listingDeets)                   #find the bed portion
    baths = regexFind('bed.? (.+?) bath',listingDeets)           #find the bath portion
    hsize = regexFind('bath[a-z]{,1} (.*?) sqft',listingDeets)   #find the house size
    lsize = regexFind('sqft (.*?) lot',listingDeets)             #find the lot size
    year = regexFind('([0-9]{4}) build',listingDeets)            #find the year built

    return [beds,baths,hsize,lsize,year]
    
def GetStories(attrs):
    """returns a list of information dependent on the value of i"""
    numStories = regexFind(r'Property Style: ([^A-Za-z\s]+)',attrs)
    if numStories is np.nan:             #this info could be in the Property Style section
        numStories = regexFind(r'Interior Levels: ([^A-Za-z\s]+)',attrs)
        if numStories is np.nan:         #or in the Interior Levels section
            numStories = regexFind(r'Exterior Stories: ([^A-Za-z\s]+)',attrs)
            if numStories is np.nan:     #or in the Exterior Levels section
                numStories = 1           #default number of stories = 1
    return numStories           
    
def GetDate(line):
    """Gets the date from the text accounting for noisy inputs. 
    If the year only has 2 digits, then we check to see if it is < 20. 
    If it is, it's in the 21st century"""
    foundDate = regexFind(r"\s{,1}\d{1,2}/\d{1,2}/\d{2,4}\s*",line)
    if foundDate is not np.nan:
        n=0
        date = ''
        for day in foundDate:
            if day in '0123456789/':
                if day == '/':
                    if len(date) == 1:
                        date='0'+date
                    elif len(date) == 4:
                        date = date[:3]+'0'+date[3:] 
                date+=day
                n+=1
        if len(date) < 10:
            year = date[-2:]
            if int(year) < 20:
                year = '20'+year
            else:
                year = '19'+year
            date = date[:-2]+year
    return date
    
def GetPrice(line):
    """Finds the price out of the line of info"""
    if type(line) != str:
        return np.nan
    try:
        return regexFind(r'\$(\S+)',line)
    except Exception as ex:
        print('Get Price Error')
        print(ex,type(ex))
        return np.nan
        
def LookatHouses(houses,index,state):
    """Scrapes all of the data from the page that contains the links to houses as well as those pages.
    Inputs:
        houses: a list of tags that contain the links to click on
        index: which index I'm at inside of the houses list
    Returns:
        df: a pd dataframe containing all of the scraped information we want
        index: the index at which we stopped scraping houses
    """
    time.sleep(0.6)
    lhouses = len(houses)
    #currentCity = browser.find_element_by_class_name("address-line-2").find_elements_by_css_selector('a')[0].text
    try:
        while True:  
            try:
                house = houses[index]   #get the next house
            except IndexError:
                print('We hit the last house at',index,'in the city of:',browser.find_element_by_class_name("address-line-2").find_elements_by_css_selector('a')[0].text)
                break
            try:  
                house.click()   #click into it
            except exceptions.StaleElementReferenceException as ex:
                print('poop1 -- House index:',index,)
                time.sleep(1)   #it might break because the page didn't navigate back to the main page before we clicked
                                #Wait a bit, navigate out and try again
                try:
                	browser.find_element_by_class_name("transparent-header").find_element_by_css_selector("a").click()
                except exceptions.ElementNotVisibleException as ex:
                    print('2')
                    time.sleep(0.5)
                except exceptions.NoSuchElementException as ex:
                    print('3')
                houses = browser.find_elements_by_class_name('buffer')[0].find_elements_by_css_selector('a')
                if len(houses) > lhouses:                   
                    lhouses = len(houses)
                house = houses[index]
                house.click()
            time.sleep(0.8)
            if houseIndex % 15: #need some extra time every now and again to give the page a rest
                time.sleep(1.25)

            try:    #get all of the details stored in the listing details section
                listingDeets = browser.find_element_by_class_name("listing-details").text
                lDeetsList = ParseListingDeets(listingDeets)  
               # time.sleep(0.6)   
            except exceptions.NoSuchElementException as ex:
                print('poop2 --',type(ex),'--',len(lDeetsList))
                #if it breaks, the page ended up being a new page instead of 
                # a popup, so navigate back
                browser.back()
                time.sleep(2)
                continue   
        #get all of the address info and add city, zipcode to our list
            addressDeets = browser.find_element_by_class_name("address-line-2").find_elements_by_css_selector('a')
            lDeetsList += [addressDeets[0].text,state,addressDeets[2].text]
       #get all of the housing attributes and add it to the list
            housingAttrs = browser.find_elements_by_class_name("home-attributes-list")
            #gets number of stories the house has and adds it to list (defaults to 1)
            lDeetsList += [GetStories(housingAttrs[0].text+' '+housingAttrs[1].text)]
        
        #get the sold Date and Price
            lDeetsList.append(browser.find_element_by_class_name("display-1").text)
        #get the foreclosure details
            soldDateInfo = browser.find_elements_by_class_name('margin-bottom-0')[1].text
            if 'Foreclosure' in soldDateInfo:
                lDeetsList.append(True)
            else:
                lDeetsList.append(False)
            lDeetsList.append(GetDate(soldDateInfo))

        #get the date it was put on the market
            try:
                daysOnMarketFullText = browser.find_element_by_class_name("js-time-since-today").get_attribute('title')
                lDeetsList += [GetDate(daysOnMarketFullText)]

            except exceptions.NoSuchElementException as ex:
                print('poop6 --',type(ex),'-- There probably wasn\'t a hover option for \'DaysOnWebsite\'.')
                lDeetsList += [np.nan]
        #get the walkscore, internet speed, and utility cost info
            miscScores = browser.find_elements_by_class_name("display-2")
            scores = [np.nan,np.nan,np.nan]         # [walkscore,internetspeed,utilities]    
            internetFinder = re.compile(r'[0-9]+ [a-zA-Z]{1,5}')
            utilityFinder = re.compile(r'\$[0-9]+ .{3,4}')            
            for score in miscScores:
                if bool(internetFinder.search(score.text)):
                    scores[1] = score.text
                elif bool(utilityFinder.search(score.text)):
                    scores[2] = score.text
                else:
                    scores[0] = score.text
            lDeetsList += scores
        #get the original listing price
            try:
                # Tries to click the 'Show more' button. If 'Show' isn't in the
                # string (!= -1), don't try finding data because it's not there.
                temp = browser.find_elements_by_class_name('btn-link')[-1].text
                if temp.find('Show') != -1:
                    browser.find_elements_by_class_name('btn-link')[-1].click()
                    time.sleep(0.6)
                    priceRows = browser.find_elements_by_class_name("history-event")
                    InitialListing = [x for x in priceRows if "Active" in x.text]

                    if len(InitialListing) == 0:
                        time.sleep(0.6)
                        priceRows = browser.find_elements_by_class_name("history-event")
                        InitialListing = [x for x in priceRows if "Active" in x.text]
                        if len(InitialListing) == 0:
                            InitialListing = ['']
                        else:
                            InitialListing = InitialListing[-1].text
                else:        
                    InitialListing = ['']

            except exceptions.NoSuchElementException as ex:
                print('poop3 --',type(ex),"-- If the problem isn't a missing 'Show more' button, then I'm stumped.")       
            finally:
                lDeetsList.append(GetPrice(InitialListing))    
            try:    
        #get the school scores
                schoolScores = browser.find_elements_by_class_name("school-score")[:3]
                for score in schoolScores:
                    lDeetsList.append(score.text)
                for i in range(len(columnList) - len(lDeetsList)):
                    lDeetsList.append(np.nan)
                df.loc[index] = lDeetsList
            except Exception as ex:
                print('poop4 --',type(ex),"-- Not sure what could have caused an exception here.")
            index +=1
    #navigate back 
            try:
                browser.find_element_by_class_name("transparent-header").find_element_by_css_selector("a").click()
            except exceptions.NoSuchElementException as ex:
                print('poop5 --',type(ex),'--',ex)
                time.sleep(0.5)#if it didn't work, then click back instead
                browser.back()
            time.sleep(2)
    finally:    #at the end of it all, return what we want to keep
        return df,index
    
for startingURL in stateURLs2Scrape:        
    fails = []
    folderName = "{}CSVs".format(startingURL[-2:])
    if not os.path.exists(folderName):
    	os.makedirs(folderName)
    numMissedHouses = 0
    #open a chrome browser and make it full screen
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--incognito")
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.maximize_window()
    try:
    #get each of the links we want to look at
        linkIndex = 0
        first = True
        while True:
            browser.get(startingURL)
            time.sleep(2)
                #get all of the links of the city's in that state
            link = browser.find_elements_by_css_selector("a")[36+linkIndex]
            linkIndex += 1
            cityName = link.get_attribute('href')[28:-5]
        #navigate to the page
            link.send_keys(Keys.RETURN)
        #filter so we only get houses
            if first:
                filters = browser.find_elements_by_class_name("dropdown-toggle")[4]
                filters.click()
                badFilters = browser.find_elements_by_class_name('dropdown-menu')[4].find_elements_by_css_selector('li')[1:]
                for f in badFilters:
                    f.click()
                    time.sleep(1)
                first = False
             #initialize a new dataframe for each city so that we can save them individually 
            df = pd.DataFrame(columns=columnList)
            index = 0
            #locate each house and iterate through all of them getting the wanted info
            houseIndex = 0
            
            # won't break IF the index is out of index
            try:
                houses = browser.find_elements_by_class_name('buffer')[0].find_elements_by_css_selector('a')
            except exceptions.WebDriverException as ex:
                print(type(ex),'in',cityName,'at index:',houseIndex)
            
            lhouses = len(houses)

            # click on each house and get the info. Then return the dataframe so we can save it 
            # **Added state to this so that it would be right next to city**   
            df,index = LookatHouses(houses,houseIndex,startingURL[-2:])
                #if this condition is true, then the page didn't get to load all of the way before the program tried to scrape
                #in this case, the program aborts and returns the number of misses
            if lhouses > 0 and index < lhouses:
                fails.append("Exception at index {} out of {} in the city {}\n".format(index,lhouses,cityName))
                numMissedHouses += (lhouses - index)
                    
            time.sleep(1)
            #save the new dataframe as a csv
            df.to_csv("{}/{}.csv".format(folderName,cityName))
    finally:    
        #at the end write the fails file
        fails.append("Overall, we missed scraping {} houses".format(numMissedHouses))
        with open('{}/{}Fails.txt'.format(folderName,startingURL[-2:]),'w') as f:
            for fail in fails:
                f.write(fail)
#browser.close()

#pagination pagination is the class for changing pages 
