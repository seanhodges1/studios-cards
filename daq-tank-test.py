# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import dash
from dash.dependencies import Input, Output
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash(__name__)

app.layout = html.Div([
    
    daq.Tank(
        id="my-tank",
        value=3,
        label='Tank label',
        labelPosition='bottom',
        scale={'interval': 2, 'labelInterval': 2,
               'custom': {'5': 'Set point'}},
        style={'margin-left': '50px'}
    ), 
    dcc.Interval(
        id='update', 
        n_intervals=0, 
        interval=1000*300)  

])



@app.callback(Output('my-tank', 'value'), Input('update', 'n_intervals'))

def update_tank(value):
    value=5
    return value


if __name__ == '__main__':
    app.run_server(debug=True)