# Author: Laura Gutierrez Funderburk
# Created on: August 2020
# Last modified on: September 17 2020

import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from ipywidgets import interact, interact_manual, widgets, Layout, VBox, HBox, Button
from IPython.display import display, Javascript, Markdown, HTML, clear_output
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go


def rerun_cell( b ):
    
    display(Javascript('IPython.notebook.execute_cell_range(IPython.notebook.get_selected_index()+1,\
    IPython.notebook.get_selected_index()+2)'))   

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
def plot_infections(Delta, beta, mu, epsilon,gamma,alpha,delta):
    
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
        None
    
    """
    
    # Run simulation
    seir_simulation = run_seir_model(Delta, beta, mu, epsilon,gamma,alpha,delta)
    
    # Create layout
    layout = dict( xaxis=dict(title='Time (days)', linecolor='#d9d9d9', mirror=True),
              yaxis=dict(title='Number of people', linecolor='#d9d9d9', mirror=True))
    
    fig = go.Figure(layout=layout)
    
#    fig.add_trace(go.Scatter(x=seir_simulation["Time (days)"], y=seir_simulation["Susceptible"],
#                        mode='lines',
#                        name='Susceptible'))
    
    fig.add_trace(go.Scatter(x=seir_simulation["Time (days)"], y=seir_simulation["Exposed"],
                        mode='lines',
                        name='Exposed'))
    
    fig.add_trace(go.Scatter(x=seir_simulation["Time (days)"], y=seir_simulation["Infectious"],
                    mode='lines',
                    name='Infectious'))
    
    fig.add_trace(go.Scatter(x=seir_simulation["Time (days)"], y=seir_simulation["Recovered"],
                        mode='lines', name='Recovered'))

    fig.add_trace(go.Scatter(x=seir_simulation["Time (days)"], y=seir_simulation["Deaths"],
                        mode='lines', name='Deaths'))

    fig.update_layout(title_text="Projected Susceptible, Exposed, Infectious, Recovered, Deaths")

    fig.show();
    

def tinker_beta(beta):
    """
    This function creates an interactive plot simulating the S.E.I.R. model
      that allows the user to modify the beta parameter only, while leaving the remaining parameters
      in the model constant
    
    Args:
        beta (float): rate of contact with infectious
        
    Returns:
        None
    """
    epsilon = 0.1
    alpha = 0.005
    gamma = 0.1
    mu = 0
    Delta = 0
    delta = 0.00
    numerator = beta*epsilon
    denominator = (alpha + gamma + mu)*(epsilon + mu)
    print("Each infection will generate approximately", numerator/denominator , "new infections.")
    plot_infections(Delta, beta, mu, epsilon, gamma, alpha,delta)
    
    
def tinker_beta_alpha(beta,alpha):
    """
    This function creates an interactive plot simulating the S.E.I.R. model
      that allows the user to modify the beta and alpha parameters only, while leaving the remaining parameters
      in the model constant
    
    Args:
        beta (float): rate of contact with infectious
        alpha (float): rate of death due disease
        
    Returns:
        None
    """
    epsilon = 0.1
    gamma = 0.1
    mu = 0
    Delta = 0
    delta = 0.00
    numerator = beta*epsilon
    denominator = (alpha + gamma + mu)*(epsilon + mu)
    print("Each infection will generate approximately", numerator/denominator , "new infections.")
    plot_infections(Delta, beta, mu, epsilon, gamma, alpha,delta)
    
    
def plot_model(button):
    
    """
    This function creates an interactive plot simulating the S.E.I.R. model
    all parameters for model (excluding initial conditions) are provided by the user
    via the use of ipywidgets (float sliders)
    
    Args:
        button (ipywidgets button)
        
    Returns:
        None
    """
    
    # Obtain positional value for parameters from all_the_widget list (see main program for details)
    beta = all_the_widgets[0].value
    eps = all_the_widgets[1].value
    gamma = all_the_widgets[2].value
    alpha = all_the_widgets[3].value
    Delta =  all_the_widgets[4].value
    mu =  all_the_widgets[5].value
    delta =  all_the_widgets[6].value
    # Compute R0 
    numerator = beta*eps
    denominator = (alpha + gamma + mu)*(eps + mu)
    # Clear plot for next use
    clear_output()
    # Display user menu
    display(tab)
    # Plot simumation
    print("Each infection will generate approximately", numerator/denominator , "new infections.")
    plot_infections(Delta, beta, mu, eps,gamma,alpha,delta)
    
    
    
if __name__ == "__main__":
    
    
    # A grid of time points (in days)
    t = np.linspace(0, 750, 750)
    
    # Widget style
    style = {'description_width': 'initial'}
   
    # Create interactive menu with parameters
    all_the_widgets = [widgets.FloatSlider(
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
    CD_button = widgets.Button(
        button_style='success',
        description="Run Simulations", 
        layout=Layout(width='15%', height='30px'),
        style=style
    )    

    # Connect widget to function - run subsequent cells
    CD_button.on_click( plot_model )

    # user menu using categories found above
    tab3 = VBox(children=[HBox(children=all_the_widgets[0:3]),HBox(children=all_the_widgets[3:6]),
                          HBox(children=all_the_widgets[6:]),
                          CD_button])
    tab = widgets.Tab(children=[tab3])
    tab.set_title(0, 'Choose Parameters')
    
    clear_output()
    
    
     # Question 0
    student_text0 = widgets.Textarea( value='', 
                                     placeholder='Write your answer here. Press Record Answer when you finish.', 
                                     description='', disabled=False , layout=Layout(width='100%', height='75px') )
    student_button0 = widgets.Button(button_style='info',
                                     description="Record Answer", 
                                     layout=Layout(width='15%', height='30px'))

    student_button0.on_click( rerun_cell ) 
    
    # Question 1
    student_text1 = widgets.Textarea( value='', 
                                     placeholder='Write your answer here. Press Record Answer when you finish.', 
                                     description='', disabled=False , layout=Layout(width='100%', height='75px') )
    student_button1 = widgets.Button(button_style='info',
                                     description="Record Answer", 
                                     layout=Layout(width='15%', height='30px'))

    student_button1.on_click( rerun_cell ) 
    
    # Question2 
    student_text2 = widgets.Textarea( value='', 
                                     placeholder='Write your answer here. Press Record Answer when you finish.', 
                                     description='', disabled=False , layout=Layout(width='100%', height='75px') )
    student_button2 = widgets.Button(button_style='info',
                                     description="Record Answer", 
                                     layout=Layout(width='15%', height='30px'))

    student_button2.on_click( rerun_cell ) 
    
    # Question 3
    student_text3 = widgets.Textarea( value='', 
                                     placeholder='Write your answer here. Press Record Answer when you finish.', 
                                     description='', disabled=False , layout=Layout(width='100%', height='75px') )
    student_button3 = widgets.Button(button_style='info',
                                     description="Record Answer", 
                                     layout=Layout(width='15%', height='30px'))

    student_button3.on_click( rerun_cell ) 
    
    
    

