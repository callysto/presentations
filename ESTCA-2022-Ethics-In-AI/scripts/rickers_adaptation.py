# Code authors: Bryce Haley, Laura G. Funderburk
# Model from Cycles, stochasticity and density dependence in pink salmon population dynamics (2011) by Krkosek et al. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3107658/
# Last modified: Jan 6 2021 

"""
This script contains code that implements a fish trap using an adaptation of the Ricker model, where the user can modify a quota (how much fish to harvest 

on any given year), and observe the population size for pink salmon (even/odd year lineages)

"""
import numpy as np
import pandas as pd
import math
import plotly.graph_objects as go
from copy import copy
from plotly.subplots import make_subplots
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets


def split_list(lst):
    even_list = lst[::2]
    odd_list = lst[1::2]
            
    return {'odds': odd_list, 'evens': even_list}

class Fishtrap:
    """Fishtrap object will hold the model, variables and produce plots showing the population dynamics of our salmon."""
    def __init__(self, r=1.36,  b=0.00136, c=0.8, N1=700, N2=300):
        self.r = r
        self.b = b
        self.c = c
        self.N = [N1, N2]
        self.t = 2
        self.harvest_available = 0
        self.harvest_record = [0,0]


    def run_step(self, N=None):
        """Run the model to produce the next years population abundance.
        input:
            N: array holding the population abundance record for the fish.
        return:
            The next years abundance of fish"""
        if N is None:
            N = self.N
        t = len(N)
        r = self.r
        c = self.c
        b = self.b
        
        return N[t-2] * math.exp(r - (b * N[t-2]) - (c * b * N[t-1]))
        
    def run_year(self, quota):
        """Run the model for one year and harvest fish set by Harvest.
        input: 
            quota: integer amount represnting the maximum number of fish harvested in this year
        raises:
            ValueError: if quota is not a non-negative integer"""
        if(isinstance(quota, int)):
            if(quota >= 0):
                self.N.append(max(0, math.floor(self.harvest_available - quota)))
                self.harvest_record.append(min(quota, math.floor(self.harvest_available)))
                self.t += 1
                self.harvest_available = 0 
            else:
                # quota is negative
                raise ValueError("quota must be a non-negative number.")
        else:
            #quota is not an integer
            raise ValueError("quota must be a valid integer. Try Again.")
            
    def make_figure(self, N):
        """Produce a simple line plot.
        returns: plotly.go figure object"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=N['odds'], x=np.linspace(1, 11, 6), name='odd year population',
            hovertemplate = 'Year: %{x}'+ '<br>Pop: %{y}'))
        fig.add_trace(go.Scatter(y=N['evens'], x=np.linspace(2, 12, 6), name='even year population',
            hovertemplate = 'Year: %{x}'+ '<br>Pop: %{y}'))
        fig.add_shape(type='line',
                xref='x', yref='paper',
                x0=2.5, y0=0, x1=2.5, y1=1,
                line=dict(color='Black', width=3))
        return fig

    def make_pieplot(self):
        "produces a pieplot showing the total fish harvested"
        split_harvest = split_list(self.harvest_record)
        labels = ['odd year', 'even year']
        values = [sum(split_harvest['odds']), sum(split_harvest['evens'])]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values, title='Fish Harvested by Population')])
        fig.update_traces(hoverinfo='label', textinfo='value')
        return fig

    def project_pop(self):
        """Project population without mutating the model's state (no harvesting).
        returns: a dictionary showing both odd an even years' population growth without harvesting"""
        M = self.N[0:2]
        for x in range(10):
            M.append(self.run_step(M))
        split_N = split_list(M)
        
        fig = self.make_figure(split_N)
        fig.update_layout(title='Projected Fish Population')

        return fig

    def run_ten_years_quota(self, quota):
        """runs the model with quota and changes the instances values to match
        input:
            quota"""
        #TODO: Experiment with changing to while(self.harvest_available != 0)
        # This would allow us to see how long we could sustain a population at a given quota level
        flag=True
        if flag==True:
            for x in range(10):
                self.harvest_available = self.run_step()
                self.run_year(quota)
        else:
            
            self.harvest_available = self.run_step()
            while self.harvest_available !=0:
                self.harvest_available = self.run_step()
                self.run_year(quota)
                
    def model_with_quota(self, quota):
        """Run the model for 10 years with a set quota
        input:
            quota: number of fish that can be harvested each year
        returns:
            plotly go figure object"""
        self.run_ten_years_quota(quota)
        split_N = split_list(self.N)
        fig = self.make_figure(split_N)
        fig.update_layout(title='Fish Population')
        return fig

    def show_results(self):
        """Create side by side result plots using the data in the instance
        Returns:
            plotly go figure holding the line chart and pie graph"""

        N = split_list(self.N)
        # create subplot
        fig = make_subplots(rows=1,cols=2,
                subplot_titles=('Fish population', 'Harvested fish'),
                specs=[[{'type': 'xy'}, {'type': 'pie'}]])
        #Add population line graph
        fig.add_trace(go.Scatter(y=N['odds'], x=np.linspace(1, 11, 6), name='odd year population',
                hovertemplate =
                'Year: %{x}'+ '<br>Pop: %{y}'),
                row=1, col=1)
        fig.add_trace(go.Scatter(y=N['evens'], x=np.linspace(2, 12, 6), name='even year population',
                hovertemplate =
                'Year: %{x}'+ '<br>Pop: %{y}'),
                row=1, col=1)
        fig.update_xaxes(title_text="year", row=1, col=1)
        fig.update_yaxes(title_text="population", row=1, col=1)

        # cannot use 'paper' as yref due to bug in sublplot.
        fig.add_shape(type='line',
                xref='x', yref='y',
                x0=2.5, y0=-10, x1=2.5, y1=1000,
                line=dict(color='Black', width=3),
                row=1, col=1)

        # create pie chart
        colors = ['#636EFA', '#EF553B']        
        labels = ['total odd year harvest', 'total even year harvest']
        M = split_list(self.harvest_record)
        values = [sum(M['odds']), sum(M['evens'])]
        fig.add_trace(go.Pie(labels=labels, values=values, hoverinfo='label', textinfo='value', marker=dict(colors=colors)), 
                row=1, col=2)

        # add title
        fig.update_layout(title_text='Results') 
        
        return fig

    def reset(self):
        """brings instance to default state"""
        self.N = self.N[0:2]
        self.t = 2
        self.harvest_available = 0
        self.harvest_record = [0,0]

    def make_output_quota(self, quota):
        """resets the instance, runs the model and creates subplot output.
        shows the outputs.
        input: 
            quota(int) - the number of fish harvested at the river-mouth per year
        returns:
            plotly subplot showing the results
        """
        self.reset()
        self.run_ten_years_quota(quota)
        return self.show_results()
