# Authors: Rachel Dunn, Laura GF, Anouk de Brouwer, Courtney V, Janson Lin
# Date created: Sept 12 2020
# Date modified: January 28 2022

# Import libraries 
from datetime import datetime
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import sys
from dateutil.relativedelta import relativedelta

##usage: python web_scrapping.py https://www.waterlevels.gc.ca/eng/data/table/2020/wlev_sec/7965 2020-01-01 2020-04-30

def get_tide_data(url: str) -> []:
    
    """
    This function performs a query to a REST API
    
    Parameters:
    ----------
        url (string) contains url to be queries
        
    Returns:
    --------
        jsonResponse (list) contains response from query in a list, stored in JSON format
    
    """
    
    try:
        response = requests.get(url)
        # access JSOn content
        jsonResponse = response.json()
        return jsonResponse

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
        
        
def build_url(area_id: str) -> str:
    
    """
    This function constructs url for download
    
    Parameters:
    -----------
        area_id (string) code obtained from https://tides.gc.ca/en/web-services-offered-canadian-hydrographic-service 
            see station API https://api-iwls.dfo-mpo.gc.ca/api/v1/stations
            
    Returns:
    --------
        data_url (string) full url from Tides API with the last 6 days from today
    """

    # Get today's date and date 6 days from today's date
    now = datetime.now()
    one_month = now + relativedelta(days=-6)

    # Format date into YYYY-MM-DD format
    startTime = one_month.strftime("%Y-%m-%d")
    endTime = now.strftime("%Y-%m-%d")

    # Build url
    from_date = startTime
    to_date = endTime
    data_url = f"https://api-iwls.dfo-mpo.gc.ca/api/v1/stations/{area_id}/data?time-series-code=wlp&from={from_date}T00:00:00Z&to={to_date}T00:30:00Z"
    
    return data_url

def build_df(area_id: str) -> pd.DataFrame:
    """
    This function performs query and saves result as a dataframe
    
    Parameters:
    -----------
        area_id (string) code obtained from https://tides.gc.ca/en/web-services-offered-canadian-hydrographic-service 
            see station API https://api-iwls.dfo-mpo.gc.ca/api/v1/stations
            
    Returns:
    --------
        data_df (dataframe object) contains JSON response in dataframe format after performing query
    """
    
    # Building url and performing query
    data_source = build_url(area_id)
    jsonResponse = get_tide_data(data_source)
    
    # Flatten JSON response into a dataframe format
    data_df = pd.json_normalize(jsonResponse)
    
    # Store file and time stamp it
    now = datetime.now()
    endTime = now.strftime("%Y-%m-%d")
    data_df.to_csv(f'./resources/{endTime}_tideData.csv')
    
    return data_df


if __name__ == "__main__":

    #parse arguments
    str(sys.argv)
    area_id = str(sys.argv[1])
    
    build_df(area_id)
