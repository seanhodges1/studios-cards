# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import datetime as dt
import urllib.parse
from datetime import datetime

import dash
import dash_bootstrap_components as dbc  # conda install -c conda-forge dash-bootstrap-components
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytz
from dash.dependencies import Input, Output

# import requests
# import sys
import web_service as ws

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


def build_card(id,sites):
    site = sites[id]
    river_card = dbc.Card([
        dbc.CardHeader(
                        id='card-'+str(id),
                        #children=site,
                        style={'padding': '2px'},
                        children=dbc.Button(site, color="link", style={'font-size':'0.8em'}),
        
                    ),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.P(['Height change (m) last 24 hrs'])
                ],
                style={'font-size':'0.75em'}
                ),
                dbc.Col([
                    dcc.Graph(id='indicator-graph-'+str(id), figure={},
                        config={'displayModeBar':False}
                    )
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='daily-line-'+str(id), figure={},
                        config={'displayModeBar':False}
                    )
                ])
            ])
        ],
        #style = {"width":"24rem"},
        className = "mt-3")
    ])
    return river_card


def build_card_indicator(id, sites, data):
    site = sites[id]
    sitedata = data.query("SiteName == '" + site + "'")
    day_start = sitedata['Value'].iloc[0] # first element 
    day_end = sitedata['Value'].iloc[-1] # last element 
    
    fig = go.Figure(go.Indicator(
        mode =  'delta',
        value = day_end,
        delta = {'reference': day_start, 'relative': False, 'valueformat':'0.3f'}
       
    ))
    fig.update_traces(delta_font={'size':14})
    fig.update_layout(height=30,width=70)

    if day_end >= day_start:
        if day_end-day_start>=1:
            fig.update_traces(delta_increasing_color="IndianRed")
        elif day_end-day_start>=0.2:
            fig.update_traces(delta_increasing_color="orange")
        else:
            fig.update_traces(delta_increasing_color="green")
    elif day_end < day_start:
        fig.update_traces(delta_decreasing_color="CornflowerBlue")
    return fig


def build_card_graph(id, sites, data):
    site = sites[id]
    sitedata = data.query("SiteName == '" + site + "'")
    fig = px.line(sitedata, x='Time', y='Value',
        range_y = [sitedata['Value'].min(), sitedata['Value'].max()],
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

    day_start = sitedata['Value'].iloc[0] # first element 
    day_end = sitedata['Value'].iloc[-1] # last element 
    
    if day_end >= day_start:
        if day_end-day_start>=1.0:
            fig.update_traces(fill='tozeroy',line={'color':'IndianRed'})
        elif day_end-day_start>=0.2:
            fig.update_traces(fill='tozeroy',line={'color':'orange'})
        else:
            fig.update_traces(fill='tozeroy',line={'color':'green'})
    elif day_end < day_start:
        fig.update_traces(fill='tozeroy',line={'color':'CornflowerBlue'})

    return fig

# Pulling water level data from Hilltop Server
data = get_all_stage_data()
data["Time"] = pd.to_datetime(data["Time"],infer_datetime_format=True)
data["Value"] = pd.to_numeric(data["M1"])/1000.0
#data = data.query("SiteName == 'Makakahi at Hamua'")
sites = list(np.sort(data.SiteName.unique()))
identifiers = [72,69,3,26,4,6,11,27,25,24,31,35,39]

# Attribute icons
# <div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
# <div>Icons made by <a href="https://www.flaticon.com/authors/smashicons" title="Smashicons">Smashicons</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>

# Create an instance of the dash class
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# --- This line added for deployment to heroku
# server = app.server
# ---

row_1 = dbc.Row(
    [
        dbc.Col([
            build_card(72,sites)            
        ]),
        dbc.Col([
            build_card(69,sites)
        ]),
        dbc.Col([
             build_card(3,sites)
        ]),
        dbc.Col([
             build_card(26,sites)
        ]),
    ],
    className="mb-4",
)


row_2 = dbc.Row(
    [
        dbc.Col([
            build_card(4,sites)            
        ]),
        dbc.Col([
            build_card(6,sites)
        ]),
        dbc.Col([
             build_card(11,sites)
        ]),
    ],
    className="mb-4",
)

row_3 = dbc.Row(
    [
        dbc.Col([
            build_card(27,sites)            
        ]),
        dbc.Col([
            build_card(25,sites)
        ]),
        dbc.Col([
             build_card(24,sites)
        ]),
    ],
    className="mb-4",
)

row_4 = dbc.Row(
    [
        dbc.Col([
            build_card(31,sites)            
        ]),
        dbc.Col([
            build_card(35,sites)
        ]),
        dbc.Col([
            build_card(39,sites)
        ]),
    ],
    className="mb-4",
)


app.layout = dbc.Container([
    html.Div([row_1, row_2, row_3, row_4]),
    dcc.Interval(id='update', n_intervals=0, interval=1000*300)
])


@app.callback(
 [
    Output('indicator-graph-72','figure'),
    Output('indicator-graph-69','figure'),
    Output('indicator-graph-3','figure'),
    Output('indicator-graph-26','figure'),
    Output('indicator-graph-4','figure'),
    Output('indicator-graph-6','figure'),
    Output('indicator-graph-11','figure'),
    Output('indicator-graph-27','figure'),
    Output('indicator-graph-25','figure'),
    Output('indicator-graph-24','figure'),
    Output('indicator-graph-31','figure'),
    Output('indicator-graph-35','figure'),
    Output('indicator-graph-39','figure'),
    ],
    Input('update', 'n_intervals')
)

def update_graph(timer):
    # perform some logic here


    output_1 = build_card_indicator(identifiers[0], sites, data)
    output_2 = build_card_indicator(identifiers[1], sites, data)
    output_3 = build_card_indicator(identifiers[2], sites, data)
    output_4 = build_card_indicator(identifiers[3], sites, data)

    output_5 = build_card_indicator(identifiers[4], sites, data)
    output_6 = build_card_indicator(identifiers[5], sites, data)
    output_7 = build_card_indicator(identifiers[6], sites, data)

    output_8 = build_card_indicator(identifiers[7], sites, data)
    output_9 = build_card_indicator(identifiers[8], sites, data)
    output_10 = build_card_indicator(identifiers[9], sites, data)
    
    output_11 = build_card_indicator(identifiers[10], sites, data)
    output_12 = build_card_indicator(identifiers[11], sites, data)
    output_13 = build_card_indicator(identifiers[12], sites, data)
    
    return output_1, output_2, output_3, output_4, output_5, output_6, output_7, output_8, output_9, output_10, output_11, output_12, output_13   
    # these variable names can be whatever you want


@app.callback(
    [
    Output('daily-line-72','figure'),
    Output('daily-line-69','figure'),
    Output('daily-line-3','figure'),
    Output('daily-line-26','figure'),
    Output('daily-line-4','figure'),
    Output('daily-line-6','figure'),
    Output('daily-line-11','figure'),
    Output('daily-line-27','figure'),
    Output('daily-line-25','figure'),
    Output('daily-line-24','figure'),
    Output('daily-line-31','figure'),
    Output('daily-line-35','figure'),
    Output('daily-line-39','figure'),
    ],
    Input('update', 'n_intervals')
)

# Line plot --------------------------------------------
def update_graph(timer):
    
    output_1 = build_card_graph(identifiers[0],sites, data)
    output_2 = build_card_graph(identifiers[1],sites, data)
    output_3 = build_card_graph(identifiers[2],sites, data)
    output_4 = build_card_graph(identifiers[3],sites, data)

    output_5 = build_card_graph(identifiers[4],sites, data)
    output_6 = build_card_graph(identifiers[5],sites, data)
    output_7 = build_card_graph(identifiers[6],sites, data)

    output_8 = build_card_graph(identifiers[7],sites, data)
    output_9 = build_card_graph(identifiers[8],sites, data)
    output_10 = build_card_graph(identifiers[9],sites, data)
    
    output_11 = build_card_graph(identifiers[10],sites, data)
    output_12 = build_card_graph(identifiers[11],sites, data)
    output_13 = build_card_graph(identifiers[12],sites, data)
    
 
    return output_1, output_2, output_3, output_4, output_5, output_6, output_7, output_8, output_9, output_10, output_11, output_12, output_13
    

if __name__ == "__main__":
    app.run_server(debug=True)
