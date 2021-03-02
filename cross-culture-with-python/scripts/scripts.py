# Authors: Bryce Haley, Laura Gutierrez Funderburk
# Created on June 2020
# Last modified on Feb 26 2021
"""
This script contains functions whose goal is to model Coast Salish Fish Traps

"""


from __future__ import print_function
from branca.element import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn
import os,sys
import math
from typing import List, Tuple
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import plotly.graph_objs as go
import ipywidgets as widgets
from ipywidgets import interact, interact_manual, widgets, Layout, VBox, HBox, Button,fixed,interactive
from IPython.display import display, Javascript, Markdown, HTML, clear_output


# global variables that act as default values for the trap inputs
default_slope = 0.17
default_inter = 6
default_radius = 25
default_height = 2
default_delta = 5
max_fish = 1000

def get_tide_values():
    """Grabs the tide values measured for one week in comox
    Returns:
        a listcontaining measured tide values for comox"""

    tide_path = os.path.join('resources', 'comox_tide.csv')
    tide_df = pd.read_csv(tide_path)
    tide_df = tide_df.drop(columns = ['PDT'])
    return tide_df.values.flatten()


def print_tide_data(tide_values):
        result_min = np.where(tide_values == min(tide_values))
        result_max = np.where(tide_values == max(tide_values))
        print("The lowest tide reaches", min(tide_values)[0],"meters on day",result_min[0][0]//24,"at",result_min[0][0]%24,"hours")
        print("The highest tide reaches",max(tide_values)[0],"meters on day",result_min[0][0]//24,"at",result_max[0][0]%24,"hours")
        
        
def create_dated_tide_plot(dataframe):
    
    try:
    
        fig = px.line(dataframe, x="Date", y="Height_m", line_shape='spline')
        fig.update_layout(title='Measured Tide Readings for ' + u'\u0294agayqs\u03B5n',
                xaxis_title = 'Time (Days Since Start)',
                yaxis_title = 'Tide Level (Meters Above Sea Level)')
        return fig
    except:
        print("Expected an objct of type dataframe with columns 'Date' and 'Height_m'. Received something different")


def create_tide_plot(timeframe="week", day=1):
    """Displays a plot of hourly tide levels for 1 week in May using readings from comox
    Args:
    
    timeframe: a string containing the word 'day' or 'week'
    if 'day' is passed a plot with a single day tide measurements will be passed
    if 'week' is passed a plot with a week tide measurements will be passed

    day: an int between 0 and 6 to select what single day will be displayed if timeframe = 'day'
    
    display: boolean, if false will return the plotly fig object. If True will display the plot and print high, low tide

    This function creates an interactive plot indicating min and max tide values,
    as well as the time when they happened.
    
    Raises: ValueError if options not entered correctly
    """

    tide_df = pd.DataFrame(get_tide_values())
    tide_df = tide_df.rename(columns = {0:'tide_level'})
    tide_df['hour'] = tide_df.index
    tide_df["day_hour"] = tide_df["hour"] % 24
    tide_df["day"] = tide_df['hour'] // 24
    try:
        timeframe = timeframe.lower()
        day = round(day)
    except:
        raise ValueError("kwarg 'timeframe' must be 'day' or 'week'.\n kwarg 'day' must be  between 0-6")

    if(timeframe == "week"):
        fig = px.line(tide_df, x="hour", y="tide_level", line_shape='spline')
        fig.update_traces(text= [f'<b>Day</b>: {x}<br><b>Hour</b>: {y}' for x,y in list(zip(tide_df['day'].values, tide_df['day_hour'].values))],
                        hovertemplate='%{text}<br>%{y:}m above sea-level')
        fig.update_layout(title='Measured Tide Readings for ' + u'\u0294agayqs\u03B5n',
                    xaxis_title = 'Time (Days Since Start)',
                    yaxis_title = 'Tide Level (Meters Above Sea Level)',
                    xaxis = dict(tickvals = tide_df.day.unique() * 24,
                                    ticktext = tide_df.day.unique()))

    elif(timeframe == "day" and 0 <= day and 6 >= day):
        tide_df = tide_df[tide_df.day == day]
        fig = px.line(tide_df, x="day_hour", y="tide_level", line_shape='spline')
        fig.update_layout(title='Measured Tide Readings for ' + u'\u0294agayqs\u03B5n' ,
                    xaxis_title = 'Time (Hours)',
                    yaxis_title = 'Tide Level (Meters Above Sea Level)')
        fig.update_traces(text= [f'<b>Day</b>: {x}<br><b>Hour</b>: {y}' for x,y in list(zip(tide_df['day'].values, tide_df['day_hour'].values))],
                        hovertemplate='%{text}<br>%{y:}m above sea-level')
    else:
        raise ValueError("kwarg 'timeframe' must be 'day' or 'week'.\n kwarg 'day' must be  between 0-6")

    return fig

def get_ratio_of_perimeter_covered(tide_level, perimeter,  radius=  25, delta= 5):
    """Given a tide level and points on the perimeter of a semi-circular trap gives the ratio of the trap under water

    Args:
        tide_level: A tide level reading in meters above sea-level
        perimeter: a list of (x,y,z) floats descriping the top of the semi-circular trap ordered in increasing x values
        radius: the radius of the semi-circular trap created
        delta: how far down the y axis the "center" of the semi-circle is from the origin

    Returns:
        a float in [0,1] that describes the amount of the trap under water.
        This calculated value ignores the warping of the semi-circle caused by the slope in the z-axis.
    """
    x_values = perimeter[0]
    y_values = perimeter[1]
    z_values = perimeter[2]

    # iterated throught the z values to find the first value underwater
    index = -1
    for i in range(len(z_values)):
        if(z_values[i] <= tide_level):
            index = i
            break;
    #if no point is underwater then return a 0 ratio underwater
    if(index == -1):
        return 0
    
    #record the x and y values for the "first" underwater point
    x = x_values[index]
    y = y_values[index]

    #find the lenth of the chord whos endpoints are (0,1) and (x,y)
    length = np.sqrt((x)**2 + (y - radius - delta)**2)
    
    #find the angle between (0,1) and (x,y) using the length of the three sides of the triangle then divide that by a half pi
    #this ratio is the ratio of the trap that is underwater
    angle = math.acos((2 * radius**2 - length**2) / (2 * radius**2))
    coverage  = angle/ (0.5 * np.pi)
    return coverage

def get_perimeter(radius= default_radius, height= default_height, delta= default_delta, slope= default_slope, intercept= default_inter):
    """Creates set of points at the top of the semi-circular trap

    Args:
        radius: an integer value that sets the radius of the trap
        height: the height from the beach surface to the top of the trap
        delta: how far down the y-axis the center of the circle is
        slope: the slope of the beach on which the trap is built
        intercept: using mean sea level as zero, the intercept for the equation of the slope of the beac
    
    returns:
        the Perimter, a 2d array:
            [0]: x values
            [1]: y values
            [2]: z values
    """
    
    theta = np.linspace(0, np.pi, 100)
    #equation for a circle
    x = radius * np.cos(theta)
    y = radius * np.sin(theta) + delta
    # equation for a line
    z = intercept + height - (slope * y)

    return [x,y,z]

def run_trap_harvesting(prev_values = [], selected_harvest= 0, radius= default_radius, height= default_height, slope= default_slope, delta= default_delta, constant_population= True):
    """Runs the model for one harvesting cycle. Where a harvesting cycle is period of time ending in the next low tide in which the trap is closed with fish inside.
    Args:
        prev_values is an array of arrays with:
            [0]: The total number of harvested fish at hour indexed
            [1]: The total number of fish in the trap at hour at hour indexed
            [2]: the total number of fish outside the trap at hour indexed
            [3]: list of the size of all harvests
        The values in this array are the history of the model. if the model is being run from the start, pass in [].
        
        selected_harvest: how many fish will be harvested this cycle. This is to be user selected
        radius: the radius of the semi-circular trap created
        height: the height of the trap
        slope: slope of the beach
        delta: how far down the y axis the "center" of the semi-circle is from the origin
        constant_population: if true the population will reset to max_fish after every harvest, else it will decrease by the number of harvested fish

    Returns:
        An 2d array containing:
            [0]: The total number of harvested fish at hour indexed
            [1]: The total number of fish in the trap at hour at hour indexed
            [2]: the total number of fish outside the trap at hour indexed
            [3]: list of the size of all harvests
            [4]: a boolean showing if the model is completed
        This returned array is shows one more cycle of harvesting than the inputed one.
        
    Throws:
        ValueError if harvesting is not a positive integer <= the number of the fish in the trap
    """

    movement_rate = 0.025
    max_fish = 1000
    perimeter_ratio = (np.pi * radius) / (np.pi * 25)
    tide_values = monthly_tide_df["Height_m"]
    perimeter = get_perimeter(radius, height, delta, slope)
    height_adjustment =1 /  min(1, height / 4)
#TODO
#if allowing users to input arbitrary values check that all the user inputs are within reasonable bounds or throw an error if they are not
    if(len(prev_values) == 0):
        #if the model is just starting
        current_free_fish = max_fish
        current_caught_fish = 0
        total_harvested = [0]
        in_trap = [0]
        out_trap = [max_fish]
        catches = []
    
    else:
        #update the model with the harvest the user selected
        total_harvested = prev_values[0]
        in_trap = prev_values[1]
        out_trap = prev_values[2]
        catches = prev_values[3]
        current_free_fish = out_trap[-1]
        current_caught_fish = in_trap[-1]
    
        try:
            selected_harvest = int(selected_harvest)
        except ValueError:
            raise ValueError("selected_harvest must be a positive integer not larger than the number of fish in the trap")

        if(selected_harvest > current_caught_fish or selected_harvest < 0):
            raise ValueError("selected_harvest must be a positive integer not larger than the number of fish in the trap")

        catches.append(selected_harvest)

        level = tide_values[len(in_trap) - 1]
        coverage = get_ratio_of_perimeter_covered(level, perimeter, radius)
        free_to_caught = current_free_fish * coverage * movement_rate * perimeter_ratio
        caught_to_free = current_caught_fish * coverage * movement_rate * perimeter_ratio * height_adjustment
        current_caught_fish = current_caught_fish - caught_to_free + free_to_caught
        current_free_fish = current_free_fish + caught_to_free - free_to_caught

        if(constant_population):
            current_free_fish = max_fish
        else:
            current_free_fish = current_free_fish + (current_caught_fish - selected_harvest)

        total_harvested.append(total_harvested[-1] + selected_harvest)
        #empty the traps and record the step after the selected harvest
        current_caught_fish = 0
        in_trap.append(current_caught_fish)
        out_trap.append(current_free_fish)

    #drop tide values already ran
    tide_values = tide_values[len(in_trap) - 1 : len(tide_values)]

    for level in tide_values:
        coverage = get_ratio_of_perimeter_covered(level, perimeter, radius)
        
        if(math.floor(current_caught_fish) != 0 and coverage == 0):
            return [total_harvested, in_trap, out_trap, catches, False]
        
        free_to_caught = current_free_fish * coverage * movement_rate * perimeter_ratio
        caught_to_free = current_caught_fish * coverage * movement_rate * perimeter_ratio
        current_caught_fish = current_caught_fish - caught_to_free + free_to_caught
        current_free_fish = current_free_fish + caught_to_free - free_to_caught
        
        total_harvested.append(total_harvested[-1])
        in_trap.append(current_caught_fish)
        out_trap.append(current_free_fish)
   
    return [total_harvested, in_trap, out_trap, catches, True]


def run_trap(radius= default_radius, height= default_height, slope= default_slope, delta= default_delta, constant_population= True):
    """Runs the fish trap model for 1 week.
    
    Args:
        radius: the radius of the semi-circular trap created
        height: the height of the trap
        slope: slope of the beach
        delta: how far down the y axis the "center" of the semi-circle is from the origin
        constant_population: if true the population will reset to max_fish after every harvest, else it will decrease by the number of harvested fish

    Returns:
        An 2d array containing:
            [0]: The total number of harvested fish at hour indexed
            [1]: The total number of fish in the trap at hour at hour indexed
            [2]: the total number of fish outside the trap at hour indexed
            [3]: list of the size of all harvests
    """
    movement_rate = 0.025
    current_free_fish = max_fish
    current_caught_fish = 0
    total_harvested = [0]
    in_trap = [0]
    out_trap = [max_fish]
    catches = []
    perimeter_ratio = (np.pi * radius) / (np.pi * 25)
    height_adjustment = 1 / min(1, height / 4)
    tide_values = get_tide_values()
    perimeter = get_perimeter(radius, height, delta, slope)
    
    #iterated through all tide levels recorded and run the model
    for level in tide_values:
        coverage = get_ratio_of_perimeter_covered(level, perimeter, radius)
        free_to_caught = current_free_fish * coverage * movement_rate * perimeter_ratio
        caught_to_free = current_caught_fish * coverage * movement_rate * perimeter_ratio * height_adjustment
        current_caught_fish = current_caught_fish - caught_to_free + free_to_caught
        current_free_fish = current_free_fish + caught_to_free - free_to_caught
        
        #if the coverage is >0 then the fish arn't trapped so "nothing" happens
        if(coverage > 0):
            total_harvested.append(total_harvested[-1])
        
        else:
            selected_harvest = math.floor(current_caught_fish)
            
            # regardless of if it was automatically selected or user selected we record the harvest level
            total_harvested.append(total_harvested[-1] + selected_harvest)
            
            if(math.floor(current_caught_fish) != 0):
                catches.append(selected_harvest)

            if(constant_population == True):
                current_free_fish = max_fish
            else:
                current_free_fish = current_free_fish + (current_caught_fish - selected_harvest)
            
            # clear the traps
            current_caught_fish = 0
        
        in_trap.append(current_caught_fish)
        out_trap.append(current_free_fish)

    return [total_harvested, in_trap, out_trap, catches]


def generate_df_from_simulation(fish_simulation):
    
    """give the data for the trap, create a plot
    Args:
        fish_simulation is a dictionary with three keys for fish which are either harvested, in the trap 
        and out of the trap, whose values are arrays from our simulation
        
    fish_simulation = {"Total harvested fish":current_results[0],
    "Total fish in the trap":current_results[1],
    "Total fish outside the trap":current_results[2]}
    
    Usage generate_df_from_simulation(fish_simulation)
    """
    df = pd.DataFrame(fish_simulation)
    
    df.columns=['Total Harvested', 'In Trap', 'Out of Trap']
    df['hour'] = df.index
    df['In Area'] = df.apply(lambda x: x['In Trap'] + x['Out of Trap'], axis=1)

    df['day'] = df['hour']//24
    df['day_hour'] = df['hour']%24
    df['In Trap'] = df['In Trap'].round()
    return df

def plot_values(fish_simulation):
    
    """give the data for the trap, create a plot
    Args:
        fish_simulation is a dictionary with three keys for fish which are either harvested, in the trap 
        and out of the trap, whose values are arrays from our simulation
        
    fish_simulation = {"Total harvested fish":current_results[0],
    "Total fish in the trap":current_results[1],
    "Total fish outside the trap":current_results[2]}
    
    Usage plot_values(fish_simulation)
    """
    
    df = generate_df_from_simulation(fish_simulation)
    # Manipulate DF a bit more
    df = df.melt(id_vars=['hour'], value_vars = ['In Trap', 'Out of Trap', 'Total Harvested', 'In Area'])
    df['value'] = df['value'].round()
    df = df.rename(columns={"value": "fish", "variable": "category"})

    fig = px.line(df, x='hour', y='fish', color='category', title="Fish Levels Throughout Harvesting")

    fig.update_traces(hovertemplate=None)

    fig.update_layout(hovermode="x",
                  yaxis_title="Number of Fish",
                 xaxis_title="Time(Days Since Start)",
                 xaxis = dict(tickvals = (df.hour // 24).unique() * 24,
                              ticktext = (df.hour // 24).unique()))

    return fig
    
def plot_caught_fish(fish_simulation):
    """Creates a plotly object displaying the fish in the trap
    Args:
        fish_simulation: a dictionary object showing the fish data to be plotted
    Returns:
        fig: a plotly figure object. Use 'fig.show()' to display plotly plot
    """
    df = generate_df_from_simulation(fish_simulation)
    
    fig = px.line(df, x="hour", y="In Trap", line_shape='spline')

    fig.update_traces(text= [f'<b>Day</b>: {x}<br><b>Hour</b>: {y}' for x,y in list(zip(df['day'].values, df['day_hour'].values))],
                            hovertemplate='%{text}<br>%{y:} fish caught')
    fig.update_layout(title='Number of Fish Trapped using circular trap model at Comox Harbour',
                        xaxis_title = 'Time (Days Since Start)',
                        yaxis_title = 'Number of trapped fish',
                        xaxis = dict(tickvals = df.day.unique() * 24,
                                        ticktext = df.day.unique()))
    
    return fig

def plot_trap(radius= default_radius, height= default_height, slope= default_slope, delta= default_delta, constant_population= True):
    """Generates a plot for the fish trap operating over 1 week

    Args:
        radius: the radius of the semi-circular trap created
        height: the height of the trap
        slope: the slope of the beach
        delta: how far down the y axis the "center" of the semi-circle is from the origin
        constant_population: if true the population will reset to max_fish after every harvest, else it will decrease by the number of harvested fish
    """

    values = run_trap(radius, height, slope, delta, constant_population)
    
    ## Build data structure
    fish_simulation = {"Total harvested fish":values[0],
                        "Total fish in the trap":values[1],
                        "Total fish outside the trap":values[2]}
    
    return plot_values(fish_simulation)
    
def plot_interactive_map(latitude, longitude, tag="Comox Valley Harbour"):
    """Creates and displays interactive plot of the area surrounnding our trap location.
        Args:
            latitude: the latitude of the center of the map
            longitude: the longtitude of the center of the map
            tag: the label given to the icon at the center of the map
    """
    # Initial coordinates
    SC_COORDINATES = [latitude, longitude]

    # Create a map using our initial coordinates
    map_osm=folium.Map(location=SC_COORDINATES, zoom_start=10, tiles='stamenterrain')

    marker_cluster = MarkerCluster().add_to(map_osm)
    folium.Marker(location = [SC_COORDINATES[0],SC_COORDINATES[1]],
                      # Add tree name
                      popup=folium.Popup(tag,sticky=True,parse_html=True),
                        tooltip='Display location name',
                      #Make color/style changes here
                      icon=folium.Icon(color='red', icon='anchor', prefix='fa'),
                      # Make sure our trees cluster nicely!
                      clustered_marker = True).add_to(marker_cluster)

    # Show the map
    display(map_osm)

def create_tide_plot_grade6(radius= default_radius, height= default_height, delta= default_delta,
                            slope= default_slope, intercept= default_inter, filename = None,
                            timeframe= 'day', day= 3):
    """Create a plot of the tide for a week superimposed with a horizontal line representing the low point of a trap.
    
    Args:
        radius: the radius of the semi-circular trap created
        height: the height of the trap
        slope: the slope of the beach
        delta: how far down the y axis the "center" of the semi-circle is from the origin
        intercept: the intercept for the eqation of the slope of the beach (y=mx+b)
        filename: if a string is entered will save the plot with the filename specified
        timeframe: if 'week' will plot for a week, if 'day' will plot for day specified
        day: an int between 0 and 6 which speficies the day to be ploted

    Returns:
        a plotly fig object.
    """

    fig = create_tide_plot(timeframe, day)

    low_point = min(get_perimeter(radius, height, delta, slope, intercept)[2])

    fig['data'][0]['showlegend']=True
    fig['data'][0]['name']='Tide Level'

    # add line to show low point of the trap
    x = fig['data'][
        0]['x']
    y = np.full(len(x), low_point)
    fig.add_scatter(x= x, y= y, name= "low point of the trap", hovertemplate=' %{y:.3f}m')

    # add text at intersection points
    fig.add_trace(go.Scatter(
        x=[8.2, 19.6],
        y=[low_point, low_point],
        mode="markers+text",
        name="Fish become trapped",
        text=["Trap Closed", "Trap Closed"],
        textposition="top right",
        hovertemplate = 'The water level is now below the trap.<br> This means fish can now be harvested.'
    ))

    fig.add_trace(go.Scatter(
        x=[13],
        y=[low_point],
        mode="markers+text",
        name="No fish are trapped",
        text=["Trap Open"],
        textposition="top right",
        hovertemplate = 'The water level is now above the trap.<br> This means fish can swim in and out of it.'
    ))

    if(isinstance(filename, str)):
        fig.write_image(filename + ".jpeg")
    elif(filename is not None):
        raise(TypeError("filename must be a string"))

    return(fig)

def create_3d_trap(radius, height, delta):
    """Creates a 3D surface plot showing the trap and the beach.
    Args:
        radius: the radius of the trap
        height: the height of the trap
        delta: how far along the beach the center of radius r circle the semicircular trap could be in
    returns:
        plt.figure() object
        """

    h = height
    r = radius

    plt3d = plt.figure().gca(projection='3d')

    # create x,y of the beach
    xx, yy = np.meshgrid(range(-35, 35), range(-25, 45))

    # calculate corresponding z
    zz = (delta - (0.17 * yy))

    # plot the beach surface
    beach_surf = plt3d.plot_surface(xx, yy, zz, alpha=0.2, color = 'brown', label = "beach")
   
   # tide_surf equations below get the legend to show
    beach_surf._facecolors2d=beach_surf._facecolors3d
    beach_surf._edgecolors2d=beach_surf._edgecolors3d


    # find data for the points on the trap on top of the beach points
    theta = np.linspace(0, np.pi, 100)
    x = r * np.cos(theta)
    y = r * np.sin(theta) + delta
    z = delta + h - (0.17 * y)
    z2 = delta - (0.17 * y)
    
    # reformat points for output
    x = np.array(tuple(zip(x, x)))
    y = np.array(tuple(zip(y, y)))
    z = np.array(tuple(zip(z, z2)))
    
    # plot the trap
    trap_surface = plt3d.plot_surface(x,y,z, label='trap')
    trap_surface._facecolors2d=trap_surface._facecolors3d
    trap_surface._edgecolors2d=trap_surface._edgecolors3d

    #format legend
    plt3d.set_xlabel('X')
    plt3d.set_ylabel('Y')
    plt3d.set_zlabel('Z')
    plt3d.set_xlim(-35,35)
    plt3d.set_ylim(-25,45)
    plt3d.legend()
    plt3d.set_title('fish trap')

    #adjust the viewing angle of the plot
    #DO NOT change notebook to allow dynamic matplotlib (VERY LAGGY)
    camera_angle = plt3d.azim
    elev_angle = plt3d.elev

    plt3d.view_init(elev = elev_angle+5, azim = camera_angle+85)

    return(plt3d)

def run_model_grade6(harvesting=True):
    """
        creates widgets allowing user to specify trap parameters then run plotting functions.
        The four slider widgets createed our:
            radius, height, location(called delta in other functions), and slope)
        the two plots created are:
            a plot of the tide superimposed with the lowest level of the trap
            a plot showing the dynamics of the fish trap
    """
    radius = widgets.IntSlider(value=25, min=4, max=30, step=1, description="Radius(m)", continuous_update=False)
    height = widgets.FloatSlider(value=2, min=0.4, max=3, step=0.2, description="Height(m)", continuous_update=False)
    location = widgets.IntSlider(value=5, min=-5, max=10, step=1, description="Location(m)", continuous_update=False)
    harvesting_percent = widgets.IntSlider(value=100, min=0, max=100, step=10, description="Percent Harvesting", continuous_update=False)

    def run(radius=25, height=2, location=5, slope=0.17, harvesting_percent=100):
        model_3d = create_3d_trap(radius, height, location)

        #fig = create_tide_plot_grade6(radius, height, location, slope, timeframe= 'week')
        fig = create_dated_tide_plot(monthly_tide_df)
        
        #lines below disable the annotations included in fig
        fig['data'][2]['y'] = None
        fig['data'][2]['x'] = None
        fig['data'][3]['y'] = None
        fig['data'][3]['x'] = None

        #loop through model cycle by cycle taking a fixed percentage of fish each cycle
        #this loops is relatively slow but would allow easy modification to allow user to select each harvest individually
        if(harvesting):
            flag = False
            current_results = []
            selected_harvest = 0
            
            while(not flag):
                current_results = run_trap_harvesting(prev_values = current_results, selected_harvest = selected_harvest,
                                                      radius= radius, height= height, slope= slope,
                                                      delta= location, constant_population = False)
                selected_harvest = math.floor(current_results[1][-1] * (harvesting_percent / 100))
                flag = current_results[4]

                fish_simulation = {"Total harvested fish":current_results[0],
                                   "Total fish in the trap":current_results[1],
                                   "Total fish outside the trap":current_results[2]}
                fig2 = plot_values(fish_simulation)
        else:
            fig2 = plot_trap(radius, height, slope, location, False)

        total = fig2['data'][2]['y'][-1]

        labels = ['Harvested Fish', 'Surviving Fish in Area']
        values = [int(total), 1000 - int(total)]

        fig3 = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig3.update_layout(title_text="Results of Harvesting")
     
        #show the plots
        plt.show()
        fig.show()
        fig2.show()
        fig3.show()

    out = widgets.interactive_output(run, {'radius': radius, 'height': height, 'location': location, 'harvesting_percent': harvesting_percent})
    display(radius, height, location, out, harvesting_percent)
    
    
from plotly.subplots import make_subplots

def run_ui_updated(radius, height, location,harvesting_percent):
    
    # Tide 
    tide_df = pd.DataFrame(get_tide_values())
    tide_df = tide_df.rename(columns = {0:'tide_level'})
    tide_df['hour'] = tide_df.index
    tide_df["day_hour"] = tide_df["hour"] % 24
    tide_df["day"] = tide_df['hour'] // 24
    

    # Trap 
    delta= location
    slope= default_slope
    intercept= default_inter
    low_point = min(get_perimeter(radius, height, delta, slope, intercept)[2])
    
    # Harvesting fish
    harvesting=True
    
    if(harvesting):
        flag = False
        current_results = []
        selected_harvest = 0

        while(not flag):
            
            current_results = run_trap_harvesting(current_results, selected_harvest,
                                                      radius, height, slope,
                                                      location, False)
            selected_harvest = math.floor(current_results[1][-1] * (harvesting_percent / 100))
            flag = current_results[4]

    # Build DF
    fish_simulation = {"Total harvested fish":current_results[0],
        "Total fish in the trap":current_results[1],
        "Total fish outside the trap":current_results[2]}

    df = generate_df_from_simulation(fish_simulation)


    # 
    fig2 = plot_values(fish_simulation)
        

    total = fig2['data'][2]['y'][-1]

    labels = ['Harvested Fish', 'Surviving Fish in Area']
    values = [int(total), 1000 - int(total)]
    # add line to show low point of the trap
    
    ##################
    #Plotting
    
    survivor_colors = ['rgb(33, 75, 99)', 'rgb(79, 129, 102)', 'rgb(151, 179, 100)','rgb(175, 49, 35)']
    
    #fig = make_subplots(rows=1, cols=4,specs=[[{"type": "scatter"},{"type": "scatter"},{"type": "scatter"}, {"type": "pie"}]])
    fig = make_subplots(rows=1, cols=2,specs=[[{"type": "scatter"}, {"type": "pie"}]])
    
    ### TIDE 

    low_point = min(get_perimeter(radius, height, delta, slope, intercept)[2])

    
    fig.add_trace(
        go.Scatter(x=monthly_tide_df["Date"], y=monthly_tide_df["Height_m"],name="Weekly Tide",
                   text= [f'<b>Day</b>: {x}<br>' \
                           for x in monthly_tide_df['Date'].values],
                        hovertemplate='%{text}<br>%{y:}m above sea-level'),
                 row=1, col=1
                 )
    
     # add line to show low point of the trap
    x = monthly_tide_df['Date']
    y = np.full(len(x), low_point)
    
    fig.add_trace(
        go.Scatter(x=x, y=np.full(len(x), low_point),name='low point of the trap',
                  hovertemplate=' %{y:.3f}m'),
        row=1, col=1
    )
    
    # FISH SIMULATION
     
        
#     fig.add_trace(
#         go.Scatter(x=df["hour"], y=df["In Trap"],mode='markers',name='Fish In Trap',
#                    marker_color=survivor_colors[2],
#                   text= [f'<b>Day</b>: {x}<br><b>Hour</b>: {y}' \
#                            for x,y in list(zip(tide_df['day'].values, tide_df['day_hour'].values))],
#                         hovertemplate='%{text}<br>%{y:} Fish'),
#         row=1, col=2
#     )
    
#     fig.add_trace(
#         go.Scatter(x=df["hour"], y=df["Out of Trap"],mode='markers',name='Fish Out of Trap',
#                    marker_color=survivor_colors[1 ],
#                   text= [f'<b>Day</b>: {x}<br><b>Hour</b>: {y}' \
#                            for x,y in list(zip(tide_df['day'].values, tide_df['day_hour'].values))],
#                         hovertemplate='%{text}<br>%{y:} Fish'),
#         row=1, col=2)
    
    # Cumulative harvested fish
    
#     fig.add_trace(
#         go.Scatter(x=df["hour"], y=df["Total Harvested"],mode='markers',
#                    name='(Cumulative) Total Harvested',
#                    marker_color=survivor_colors[0],
#                   text= [f'<b>Day</b>: {x}<br><b>Hour</b>: {y}' \
#                            for x,y in list(zip(tide_df['day'].values, tide_df['day_hour'].values))],
#                         hovertemplate='%{text}<br>%{y:} Fish'),
#         row=1, col=3
#     )
    
    
    # SURVIVOR VS HARVESTED
    

    fig.add_trace(
        go.Pie(labels=labels, values=values, name='Survivors vs Harvested Fish',
                     marker_colors=survivor_colors[0:2]),
        row=1, col=2, # Change to 4 if uncommenting the code above
    )
    
    
    fig.update_layout(height=600, width=950, title_text="Fish Trap Simulation",showlegend=True)
    fig.show()
    
    
def create_3d_trap(radius, height, delta):
    """This function creates a 3D plot of the beach along with our trap
    
    Args:
        radius (int): radius of trap
        height (int): height of trap
        delta (int): location of trap

    Returns:
        A 3D plot of the trap 
    """ 
    h = height
    r = radius

    plt3d = plt.figure(figsize=(10,10)).gca(projection='3d')

    # create x,y
    xx, yy = np.meshgrid(range(-35, 35), range(-25, 45))

    # calculate corresponding z
    zz = (delta - (0.17 * yy))

    # plot the surface

    beach_surf = plt3d.plot_surface(xx, yy, zz, alpha=0.2, color = 'brown', label = "beach")
    # tide_surf equations below get the legend to show
    beach_surf._facecolors2d=beach_surf._facecolors3d
    beach_surf._edgecolors2d=beach_surf._edgecolors3d



    theta = np.linspace(0, np.pi, 100)
    x = r * np.cos(theta)
    y = r * np.sin(theta) + delta
    z = delta + h - (0.17 * y)
    z2 = delta - (0.17 * y)

    x = np.array(tuple(zip(x, x)))
    y = np.array(tuple(zip(y, y)))
    z = np.array(tuple(zip(z, z2)))

    trap_surface = plt3d.plot_surface(x,y,z, label='trap')
    trap_surface._facecolors2d=trap_surface._facecolors3d
    trap_surface._edgecolors2d=trap_surface._edgecolors3d


    plt3d.set_xlabel('X')
    plt3d.set_ylabel('Y')
    plt3d.set_zlabel('Z')
    plt3d.set_xlim(-35,35)
    plt3d.set_ylim(-25,45)
    plt3d.legend()
    plt3d.set_title('fish trap')


    camera_angle = plt3d.azim
    elev_angle = plt3d.elev

    plt3d.view_init(elev = elev_angle+5, azim = camera_angle+85)

    return(plt3d)

def draw_results(b):
    radius = all_the_widgets[0].value
    height = all_the_widgets[1].value
    location = all_the_widgets[2].value
    harvesting_percentage = 100
    beach_flag = all_the_widgets[3].value
    clear_output()
    display(tab)  ## Have to redraw the widgets
    if beach_flag:
        create_3d_trap(radius, height, location)
    else:
        run_ui_updated(radius, height, location,harvesting_percentage)


if __name__ == "__main__":

    style = {'description_width': 'initial'}
    
    monthly_tide_df = pd.read_csv("./resources/tidesSubset.csv")

    all_the_widgets = [widgets.IntSlider(
        value=25, 
        min=4, 
        max=30, 
        step=1, 
        description="Radius of trap(m)", 
        continuous_update=False,
        style =style), widgets.FloatSlider(
        value=2, 
        min=0.4, 
        max=3, 
        step=0.2, 
        description="Heightof trap(m)", 
        continuous_update=False,
        style =style), widgets.IntSlider(
        value=5, 
        min=-5, 
        max=10, 
        step=1, 
        description="Location of trap(m)", 
        continuous_update=False,
        style =style),widgets.Checkbox(
                value=False,
                description='Plot 3D Beach Only',
                disabled=False,
                indent=False,style =style)
                      ]


    # Button widget
    CD_button = widgets.Button(
        button_style='success',
        description="Fish Trap Simulation", 
        layout=Layout(width='15%', height='30px'),
        style=style
    )
    
    # Button widget
    beach3d_button = widgets.Button(
        button_style='success',
        description="Draw Trap", 
        layout=Layout(width='15%', height='30px'),
        style=style
    )

    # Connect widget to function - run subsequent cells
    CD_button.on_click( draw_results )

    # user menu using categories found above
    tab3 = VBox(children=[HBox(children=all_the_widgets[0:2]),HBox(children=all_the_widgets[2:5]),
                          CD_button])
    tab = widgets.Tab(children=[tab3])
    tab.set_title(0, 'Choose Parameters')
   
