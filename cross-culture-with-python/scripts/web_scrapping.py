# Authors: Rachel Dunn, Laura GF, Anouk de Brouwer, Courtney V, Janson Lin
# Date created: Sept 12 2020
# Date modified: Feb 25, 2021

# Import libraries 
from datetime import datetime
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import sys
from dateutil.relativedelta import relativedelta

##usage: python web_scrapping.py https://www.waterlevels.gc.ca/eng/data/table/2020/wlev_sec/7965 2020-01-01 2020-04-30

def query_entry_pt(url):
    """This function takes as input a URL entry point and returns the complete JSON response in a REST API
    
    Input:
        - url(string): complete url (or entry point) pointing at server 
        
    Output:
        - jsonResponse(json object): JSON response associated wtih query
    
    """
    try:
        # Using GET command 
        response = requests.get(url)
        # Raise issues if response is different from 200
        response.raise_for_status()
        # access JSOn content
        return response

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
        

def parse_data(response):
    soup = BeautifulSoup(response.text, 'html.parser')

    tables = soup.find_all(class_='width-100')

    date = []
    height = []
    for table in tables:

        # get month and year from caption
        month_year = table.find("caption").text.strip()
        [month,year] = month_year.split()

        # get all cells by looking for 'align-right' class
        cell = table.find_all(class_="align-right")

        # loop over cells in table
        # every 1st cell has the day, every 2nd cell has the time, every 3rd cell has the height 
        for index in range(len(cell)):

            # get day
            if ((index % 3) == 0):
                d = cell[index].text.strip()

            # get time 
            if ((index % 3) == 1):
                t = cell[index].text.strip()

                # paste year, month, day and time together, and append to date list
                ymdt_str = '-'.join([year,month,d,t])
                #ymdt = datetime.strptime(ymdt_str,'%Y-%B-%d-%I:%M %p')
                date.append(ymdt_str)

            # get tide height
            if ((index % 3) == 2):
                height.append(cell[index].text.strip())
    return [height,date]

def build_df(height,date,startTime, endTime):

    #add lists to dataframe
    tide_data = pd.DataFrame({"Date":date,"Height_m":height})

    tide_data['Date'] = pd.to_datetime(tide_data['Date'])
    #subset dataframe to only output data between requested dates
    tide_data = tide_data[(tide_data['Date']>=startTime) & (tide_data['Date']<=endTime)]
    tide_data.to_csv(r'./resources/tidesSubset.csv', header = True)


if __name__ == "__main__":

    #parse arguments
    str(sys.argv)
    dataURL = str(sys.argv[1])
    now = datetime.now()
    one_month = now + relativedelta(months=-1)
    
    startTime = one_month.strftime("%Y-%m-%d")
    endTime = now.strftime("%Y-%m-%d")
    
    
    # Get data
    response = query_entry_pt(dataURL)
    [height,date] = parse_data(response)
    build_df(height,date,startTime, endTime)
