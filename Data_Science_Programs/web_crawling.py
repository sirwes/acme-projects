import numpy as np
import re
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from matplotlib import pyplot as plt

def scrape_books(start_page = "index.html"):
    """ Crawl through http://books.toscrape.com and extract fiction data"""
    
    # Initialize variables, including a regex for finding the 'next' link.
    base_url="http://books.toscrape.com/catalogue/category/books/fiction_10/"
    price_total = []
    count_total = []
    page = base_url + start_page                # Complete page URL.
    next_page_finder = re.compile(r"next")      # We need this button.
    current = None

    for _ in range(4):
        total = 0
        count = 0
        
        while current == None:                   # Try downloading until it works.
            # Download the page source and PAUSE before continuing.  
            page_source = requests.get(page).text
            time.sleep(1)           # PAUSE before continuing.
            soup = BeautifulSoup(page_source, "html.parser")
            current = soup.find_all(class_="price_color")
            
        #Extract the price data.
        for price in current:
            total += float(price.string.strip("Â£"))
            count += 1
    
        price_total.append(total)
        count_total.append(count)
    

        if "page-4" not in page:
            # Find the URL for the page with the next data.
            new_page = soup.find(string=next_page_finder).parent["href"]    
            page = base_url + new_page      # New complete page URL.
            current = None
        else:
            # Calculate the price average
            average_price = sum(price_total)/sum(count_total)
    return average_price


def bank_data():
    """Crawl through the Federal Reserve site and extract bank data."""
    # Compile regular expressions for finding certain tags.
    chase_finder = re.compile(r"^JPMORGAN CHASE BK NA/JPMORGAN CHASE & CO")
    boa_finder = re.compile(r"^BANK OF AMER NA/BANK OF AMER CORP")
    fargo_finder = re.compile(r"^WELLS FARGO BK NA/WELLS FARGO & CO")
    
    # Get the base page and find the URLs to all other relevant pages.
    base_url="https://www.federalreserve.gov/releases/lbr/"
    base_page_source = requests.get(base_url).text
    base_soup = BeautifulSoup(base_page_source, "html.parser")
     #find all of the tags on the page
    link_tags = base_soup.find_all(name='a', href=True)
    date_finder = re.compile(r'^[0-9]{8}')
    pages = []
    #get all of the links in those tags
    tag_hrefs = [tag.attrs["href"] for tag in link_tags]
    #check to see if the date on that tag is after December 2004
    #or if the tag is the most recent one
    for tag in tag_hrefs:
        date = date_finder.findall(tag)
        if date != []:
            year = int(date[0][:4])
            month = int(date[0][4:6])
            #if it is, save the page url
            if year >= 2004 and month == 12:
                pages.append(base_url + tag)
        elif "current/default.htm" == tag:
            pages.append(base_url + tag)
          
    # Crawl through the individual pages and record the data.
    chase_assets = []
    boa_assets = []
    fargo_assets = []
    for page in pages:
        time.sleep(1)               # PAUSE, then request the page.
        soup = BeautifulSoup(requests.get(page).text, "html.parser")

        # Find the tag corresponding to each Banks's consolidated assets.
        chase_tag = soup.find(name="td", string=chase_finder)
        boa_tag = soup.find(name="td", string=boa_finder)
        fargo_tag = soup.find(name="td", string=fargo_finder)
        for _ in range(10):
            chase_tag = chase_tag.next_sibling
            boa_tag = boa_tag.next_sibling
            fargo_tag = fargo_tag.next_sibling
        # Extract the data, removing commas.
        chase_assets.append(int(chase_tag.string.replace(',', '')))
        boa_assets.append(int(boa_tag.string.replace(',', '')))
        fargo_assets.append(int(fargo_tag.string.replace(',', '')))
        
     #now plot each of the bank's assets against time
    plt.figure()
    plt.plot(np.arange(2004,2019,1),chase_assets[::-1],'b-.',ms=10,label="Chase Bank")
    plt.plot(np.arange(2004,2019,1),boa_assets[::-1],'r-.',ms=10,label="Bank of America")
    plt.plot(np.arange(2004,2019,1),fargo_assets[::-1],'g-.',ms=10,label="Wells Fargo")
    plt.xlabel("Time")
    plt.ylabel("Consolidated Assets")
    plt.title("Comparing Bank Consolidated Assets")
    plt.legend(loc='best')
    plt.show()



def ESPNAthletes():
    """ESPN hosts data on NBA athletes at
    http://www.espn.go.com/nba/statistics. Each player has their own page with
    detailed performance statistics. For each of the five offensive leaders in
    points and each of the five defensive leaders in rebounds, extract the
    player’s career minutes per game (MPG) and career points per game (PPG).
    Make a scatter plot of MPG against PPG for these ten players.
    
    For the past ten seasons, identify which player had the most season points and find how many
points they scored during that season. Return a list of triples consisting of the season, the
player, and the points scored, (\"season year\", \"player name\", points scored).
    """
    #get the html from the page with all of the information
    base_url = 'https://www.basketball-reference.com/leagues/'
    base_page_source = requests.get(base_url).text
    base_soup = BeautifulSoup(base_page_source, "html.parser")
    #get only the tags corresponding to the last 10 seasons
    seasonTags = (base_soup.find_all('tr')[3:13])
    
    name_finder = re.compile(r'^[^\(]+')
    points_finder = re.compile(r'\([0-9\.]+\)')
    year_finder = re.compile(r'/[0-9]{4}\.')
    seasonInfo = []
    #going through each tag, get the year, player name and points scored in the top points scored section
    for season in seasonTags:
        tags = season.find_all('td')
        seasonTag = str(tags[1].a)
        year = int(year_finder.findall(seasonTag)[0][1:-1])
        
        pointsTag = tags[-4].text
        pointsScored = int(points_finder.findall(pointsTag)[0][1:-1])
        name = name_finder.findall(pointsTag)[0][:-1]
        
        seasonInfo.append((year,name,pointsScored))
       
    return seasonInfo
    
    


def ArxivSearch(search_query):
    """Use Selenium to enter the given search query into the search bar of
    https://arxiv.org and press Enter. The resulting page has up to 25 links
    to the PDFs of technical papers that match the query. Gather these URLs,
    then continue to the next page (if there are more results) and continue
    gathering links until obtaining at most 150 URLs. Return the list of URLs.

    Returns:
        (list): Up to 150 URLs that lead directly to PDFs on arXiv.
    """
    #get the base url and open the browser to that page
    base_url = 'https://arxiv.org'
    browser = webdriver.Chrome()
    browser.get(base_url)
    try:
        #get the search bar, clear whatever is there
        search_bar = browser.find_element_by_css_selector("input[placeholder='Search or Article ID']")
        search_bar.clear()
        #enter in the search query and search
        search_bar.send_keys(search_query)
        search_bar.send_keys(Keys.RETURN)
        #go to the drop down 'results per page' and select 200 results per page
        dropDown = browser.find_elements_by_id('size')[0]
        dropDown.send_keys(Keys.RETURN)
        dropDown.send_keys(Keys.DOWN)
        dropDown.send_keys(Keys.DOWN)
        dropDown.send_keys(Keys.RETURN)
        #find the go button and click it
        goButton = browser.find_elements_by_class_name('button')[-1]
        goButton.send_keys(Keys.RETURN)
        #scrape that page
        soup = BeautifulSoup(browser.page_source,'html.parser')
        #get all of the pdf tags
        urlTags = soup.find_all(href=True,text='pdf')
            
        i = 0
        urls = []
        #loop through the tags and only get up to 150 links
        for tag in urlTags:
            link = tag.attrs['href']
            if len(link) == 0:
                continue
            if link[0] == '/':
                link = base_url + link
            urls.append(link)
            i+=1
            if i == 150:
                break
        return urls
        
    except Exception:
        print('Can\'t find something')
        return []
    finally:
        browser.close()
        #close the browser
        
        


def ProjectEuler():
    """For each of the (at least) 600 problems in the archive at
    https://projecteuler.net/archives, record the problem ID and the number of
    people who have solved it. Return a list of IDs, sorted from largest to
    smallest by the number of people who have solved them. That is, the first
    entry in the list should be the ID of the most solved problem, and the
    last entry in the list should be the ID of the least solved problem.

    Returns:
        (list): problem IDs (as strings), from most solved to least solved.
    """
    #save the base url
    base_url = 'https://projecteuler.net/archives'
    try:
        problemIDs = []
        #save all of the page urls
        pages = [base_url] + [base_url+';page='+str(i) for i in range(2,14)]
            
        #go to every page and get what's on the page
        for pageUrl in pages:
            #print(pageUrl)
            page = requests.get(pageUrl).text
            time.sleep(1)               # PAUSE, then request the page.
            soup = BeautifulSoup(page,'html.parser')
            table = soup.find_all(name='table')[0]
            first = True           
            #loop through the information in the table skipping line endings and the header
            for line in table:
                if line == '\n':
                    continue
                if first:
                    first = False
                    continue
                #save all of the stuff we want
                info = line.find_all('td')
                if not info:
                    continue
                problemIDs.append((info[0].text,info[-1].text))
        #sort it from most to least and return            
        return sorted(problemIDs,key=lambda x:int(x[1]),reverse = True)
        
    except Exception:
        print('Can\'t access page')
        raise ValueError("Cannot access page")