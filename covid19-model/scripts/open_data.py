# Author: Laura Gutierrez Funderburk
# Created on: August 2020
# Last modified on: September 18 2020

import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from ipywidgets import interact, interact_manual, widgets, Layout, VBox, HBox, Button
from IPython.display import display, Javascript, Markdown, HTML, clear_output
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import requests as r


# The SEIR model differential equations.
def deriv(y, t, Delta, beta, mu, epsilon,gamma,alpha,delta):
    
    """
     This function contains a system of equations for the S.E.I.R. model assuming non constant population
     death (natural and due infection) and birth rates, as well as reinfection post recovery. 

    Args:
        y (array): contains five floating point numbers S0, E0, I0, R0, D0 where each denotes initial conditions (float)
        t (float): variable denoting time 
        Delta (float): rate of birth
        beta (float): rate of contact with infectious
        mu (float): rate of natural death
        epsilon (float): rate of infectiousness
        gamma (float): rate of recovery
        alpha (float): rate of death due disease
        delta (float): rate of reintegration into susceptible state

    Returns:
        [dS, dE, dI, dR, dD] (array)
        dS: differential equation for Susceptible
        dE: differential equation of Exposed
        dI: differential equation for Infectious
        dR: differential equation for Recovered
        dD: differential equation for Deaths
    """
    
    S, E, I, R, D = y
    N = S + E + I + R
    dS = Delta*N  - beta*S*I/N - mu*S + delta*R
    dE = beta*S*I/N - (mu + epsilon)*E
    dI = epsilon*E - (gamma + mu + alpha)*I
    dR = gamma*I - mu*R - delta*R
    dD = alpha*I 
    
    return [dS,dE, dI, dR, dD]

def run_seir_model(Delta, beta, mu, epsilon,gamma,alpha,delta):
    
    """
    This function creates an interactive plot simulating the S.E.I.R. model
    Note that susceptible has been commented out for the Callysto teacher and student notebooks
    
    Args:
        Delta (float): rate of birth
        beta (float): rate of contact with infectious
        mu (float): rate of natural death
        epsilon (float): rate of infectiousness
        gamma (float): rate of recovery
        alpha (float): rate of death due disease
        delta (float): rate of reintegration into susceptible state
        
    Returns:
        seir_simulation (pandas DataFrame): contains data resulting from our model for each of the SEIRD stages
    
    """
    # Initial number of infected and recovered individuals, I0 and R0.
    S0, E0,I0, R0 ,D0 = 37000,0,1,0,0
    # Total population, N.
    N = S0 + E0 + I0 + R0
    # Initial conditions vector
    y0 = S0,E0, I0, R0, D0
    # Integrate the SIR equations over the time grid, t.
    ret = odeint(deriv, y0, t, args=(Delta, beta, mu, epsilon,gamma,alpha,delta))
    S, E,I, R, D = ret.T

    # Build dataframe with the data from the model
    seir_simulation = pd.DataFrame({"Susceptible":S,"Exposed":E,"Infectious":I,"Recovered":R,"Deaths":D, "Time (days)":t})

    return seir_simulation

# Define a function to drop the history.prefix
# Create function drop_prefix
def drop_prefix(self, prefix):
    """
    This function applies and renames str.lstrip method to a pandas dataframe column 
    
    Args:
        prefix (str): name of column to apply function to
        
    Returns:
        self: renamed column
    """
    self.columns = self.columns.str.lstrip(prefix)
    return self



# Define function which removes history. prefix, and orders the column dates in ascending order
def order_dates(flat_df):
    """
    This function parses and cleans up dataframe obtained from requesting COVID19 data
    
    Args:
        flat_df (DataFrame object): dataframe containing COVID 19 data from Hopkins database
        
    Returns:
        final (DataFrame object): cleaned up dataframe
    """
    # Drop prefix
    flat_df.drop_prefix('history.')
    flat_df.drop_prefix("coordinates.")
    # Isolate dates columns
    flat_df.iloc[:,6:].columns = pd.to_datetime(flat_df.iloc[:,6:].columns)
    # Transform to datetim format
    sub = flat_df.iloc[:,6:]
    sub.columns = pd.to_datetime(sub.columns)
    # Sort
    sub2 = sub.reindex(sorted(sub.columns), axis=1)
    sub3 = flat_df.reindex(sorted(flat_df.columns),axis=1).iloc[:,-5:]
    # Concatenate
    final = pd.concat([sub2,sub3], axis=1, sort=False)
    return final


def fit_data(Delta, beta, mu, epsilon,gamma,alpha,delta):

    """
    This plots the actual number of reported cases of COVID19 against our simulation (infectious stage)
    
    Args:
        Delta (float): rate of birth
        beta (float): rate of contact with infectious
        mu (float): rate of natural death
        epsilon (float): rate of infectiousness
        gamma (float): rate of recovery
        alpha (float): rate of death due disease
        delta (float): rate of reintegration into susceptible state
        
    Returns:
        None
    """
    # Run simulation
    seir_simulation = run_seir_model(Delta, beta, mu, epsilon,gamma,alpha,delta)
    # Assign a date column
    seir_simulation['date'] = pd.date_range(start='01/24/2020', periods=len(seir_simulation), freq='D')
    
    # Create scatter plot for real covid 19 data
    trace3 = go.Scatter(x = non_cumulative_cases.index,y=non_cumulative_cases["TotalDailyCase"])
    # Create scatter plot for simulation (infectious stage)
    trace2 = go.Scatter(x = seir_simulation["date"],y=seir_simulation["Infectious"],yaxis='y2')
    # Create layout
    layout = go.Layout(
        title= ('First guess to fit model: infectious against number of reported cases in ' + str(country)),
        yaxis=dict(title='Daily Number of  Reported Infections',\
                   titlefont=dict(color='blue'), tickfont=dict(color='blue')),
            yaxis2=dict(title='Number of infectious members (our model)', titlefont=dict(color='red'), \
                        tickfont=dict(color='red'), overlaying='y', side='right'),
            showlegend=False)
    # Create a single figure with both scatter plots
    fig = go.Figure(data=[trace3,trace2],layout=layout)
    
    fig.show()
    
def plot_model_and_data(button):
    """
    This function creates an interactive plot with a first guess for parameters in our SEIR model
    when compared against real number of reported COVID 19 cases
    
    Args:
        button (ipywidgets button)
        
    Returns:
        None
    """
    
    # Obtain positional value for parameters from all_the_widget list (see main program for details)
    beta = all_the_widgets1[0].value
    eps = all_the_widgets1[1].value
    gamma = all_the_widgets1[2].value
    alpha = all_the_widgets1[3].value
    Delta =  all_the_widgets1[4].value
    mu =  all_the_widgets1[5].value
    delta =  all_the_widgets1[6].value
    # Compute R0 
    numerator = beta*eps
    denominator = (alpha + gamma + mu)*(eps + mu)
    # Clear plot for next use
    clear_output()
    # Display user menu
    display(tab1)
    # Plot simumation
    print("Each infection will generate approximately", numerator/denominator , "new infections.")
    fit_data(Delta, beta, mu, eps,gamma,alpha,delta)
    
if __name__ == "__main__":
    
    # PD formatting
    # Call function
    pd.core.frame.DataFrame.drop_prefix = drop_prefix
    
    # Local backup of data 
    dff = pd.read_csv("./data/confirmed.csv")
    dff = dff.set_index("Country/Region")
    dff = order_dates(dff)    
    country = "Canada"
    by_prov = dff[dff.index==country].set_index("Province/State").T.iloc[:-4,]
    by_prov["TotalDailyCase"] = by_prov.sum(axis=1)

    # This variable contains data on COVID 19 daily cases
    non_cumulative_cases = by_prov.diff(axis=0)

    t = np.linspace(0, len(non_cumulative_cases["TotalDailyCase"]), len(non_cumulative_cases["TotalDailyCase"]))

    

    ## Getting data
    try:
        print("Downloading COVID-19 data - Canada")
        API_response_confirmed = r.get("https://covid19api.herokuapp.com/confirmed")
        data = API_response_confirmed.json() # Check the JSON Response Content documentation below
        confirmed_df = pd.json_normalize(data,record_path=["locations"])

        # Flattening the data 
        flat_confirmed = pd.json_normalize(data=data['locations'])
        flat_confirmed.set_index('country', inplace=True)
        print("Download is successful!")
    except:
        
        print("COULD NOT ESTABLISH CONNECTION TO SERVER!!! USING LOCAL FILE")
          
        
    try:   
        
        # Apply function
        final_confirmed = order_dates(flat_confirmed)
        country = "Canada"
        by_prov = final_confirmed[final_confirmed.index==country].set_index("province").T.iloc[:-4,]
        by_prov["TotalDailyCase"] = by_prov.sum(axis=1)
        
        # This variable contains data on COVID 19 daily cases
        non_cumulative_cases = by_prov.diff(axis=0)
        
        t = np.linspace(0, len(non_cumulative_cases["TotalDailyCase"]), len(non_cumulative_cases["TotalDailyCase"]))

    except:
        
        print("Loading local file")
    
        
        
    style = {'description_width': 'initial'}
    
    
    
    # Create interactive menu with parameters
    all_the_widgets1 = [widgets.FloatSlider(
                            min=0, max=1, step=0.01, value=0.5,style =style,description='Beta: contact rate'),
                       widgets.FloatSlider(
                           min=0.1, max=1.0, step=.1, value=.1,style =style,description='Epsilon: infectiousness rate'),
                       widgets.FloatSlider(
                           min=0.1, max=1.0, step=.1, value=.1,style =style,description='Gamma: rate of recovery'),
                       widgets.FloatSlider(
                           min=0, max=1.0, step=.005, value=.005,style =style,description='Alpha: COVID-19 death rate'),
                      widgets.FloatSlider(
                           min=0, max=1.0, step=.005, value=0,style =style,description='Delta: Birth rate'),
                      widgets.FloatSlider(
                           min=0, max=1.0, step=.005, value=0,style =style,description='mu: Natural death rate'),
                      widgets.FloatSlider(
                           min=0, max=1.0, step=.005, value=0.005,style =style,description='delta: re-incorporation rate')]


    # Button widget
    CD_button1 = widgets.Button(
        button_style='success',
        description="Run Simulations", 
        layout=Layout(width='15%', height='30px'),
        style=style
    )    

    # Connect widget to function - run subsequent cells
    CD_button1.on_click( plot_model_and_data )

    # user menu using categories found above
    tab4 = VBox(children=[HBox(children=all_the_widgets1[0:3]),HBox(children=all_the_widgets1[3:6]),
                          HBox(children=all_the_widgets1[6:]),
                          CD_button1])
    tab1 = widgets.Tab(children=[tab4])
    tab1.set_title(0, 'Choose Parameters')
   
    


