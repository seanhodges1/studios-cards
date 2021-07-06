# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc # conda install -c conda-forge dash-bootstrap-components
from dash.dependencies import Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
# import requests
# import sys
import web_service as ws    
from datetime import datetime
import datetime as dt
import pytz
import urllib.parse

#pytz.all_timezones

def get_now():
    tz_NZ = pytz.timezone('Pacific/Auckland') 
    datetime_NZ = datetime.now(tz_NZ)
    return datetime_NZ.strftime("%Y-%m-%d %H:%M")

def start_date(daysBeforeNow=7):
    tz_NZ = pytz.timezone('Pacific/Auckland') 
    datetime_NZ = datetime.now(tz_NZ)
    day_delta = dt.timedelta(days=daysBeforeNow)
    from_date = datetime_NZ - day_delta
    return from_date.strftime("%Y-%m-%d %H:%M")

def get_data(site):
    ### Parameters
    base_url = 'http://tsdata.horizons.govt.nz/'
    hts = 'boo.hts'
    measurement = 'Stage [Water Level]'
    from_date = start_date(7)
    to_date = get_now()
    df = ws.get_data_basic(base_url,hts,site,measurement,from_date,to_date)
    # columns=['Site', 'Measurement', 'Parameter', 'DateTime', 'Value'])
    return df

def get_all_stage_data():
    base_url = 'http://tsdata.horizons.govt.nz/'
    hts = 'boo.hts'
    collection = 'River Level'
    from_date = start_date(1)
    to_date = get_now()
    df = ws.get_datatable(base_url, hts, collection, from_date=from_date, to_date=to_date)
    return df

#print("From=",start_date(),"&To=",get_now())

# Pulling water level data from Hilltop Server
data = get_all_stage_data()
data["Time"] = pd.to_datetime(data["Time"],infer_datetime_format=True)
data["Value"] = pd.to_numeric(data["M1"])/1000.0
data = data.query("SiteName == 'Makakahi at Hamua'")

# Attribute icons
# <div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
# <div>Icons made by <a href="https://www.flaticon.com/authors/smashicons" title="Smashicons">Smashicons</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>

# Create an instance of the dash class
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# --- This line added for deployment to heroku
# server = app.server
# ---

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardImg(
                    src = '/assets/png/001-A.png',
                    top = True,
                    style = {'width':'3rem'}
                ),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.P(['CHANGE (1D)'])
                        ]),
                        dbc.Col([
                            dcc.Graph(id='indicator-graph', figure={},
                                config={'displayModeBar':False}
                            )
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='daily-line', figure={},
                                config={'displayModeBar':False}
                            )
                        ])
                    ])
                ])
            ],
            style = {"width":"24rem"},
            className = "mt-3")
        ],width=6)
    ],justify='center'),

    dcc.Interval(id='update', n_intervals=0, interval=1000*300)
])


@app.callback(
    Output('indicator-graph','figure'),
    Input('update', 'n_intervals')
)

def update_graph(timer):
    day_start = data['Value'].iloc[0] # first element 
    day_end = data['Value'].iloc[-1] # last element 
    
    fig = go.Figure(go.Indicator(
        mode = 'delta',
        value = day_end,
        delta = {'reference': day_start, 'relative': True, 'valueformat':'.2%'}
    ))
    fig.update_traces(delta_font={'size':12})
    fig.update_layout(height=30,width=70)

    if day_end >= day_start:
        fig.update_traces(delta_increasing_color="green")
    elif day_end < day_start:
        fig.update_traces(delta_increasing_color="red")
        
    return fig

@app.callback(
    Output('daily-line','figure'),
    Input('update', 'n_intervals')
)

# Line plot --------------------------------------------
def update_graph(timer):
    fig = px.line(data, x='Time', y='Value',
        range_y = [data['Value'].min(), data['Value'].max()],
        height=120
        ).update_layout(margin=dict(t=0,r=0,l=0,b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis = dict(
            title=None,
            showgrid=False,
            showticklabels=False
        ),
        xaxis = dict(
            title=None,
            showgrid=False,
            showticklabels=False
        )
    )

    day_start = data['Value'].iloc[0] # first element 
    day_end = data['Value'].iloc[-1] # last element 
    
    if day_end >= day_start:
        fig.update_traces(fill='tozeroy',line={'color':'green'})
    elif day_end < day_start:
        fig.update_traces(fill='tozeroy',line={'color':'red'})

    return fig




if __name__ == "__main__":
    app.run_server(debug=True)
