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
    from_date = start_date(0.25)
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
                    html.P(['Height change (m) last 6 hrs'])
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
            fig.update_traces(fill='tozeroy',line={'color':'CornflowerBlue'})
        elif day_end-day_start>=0.2:
            fig.update_traces(fill='tozeroy',line={'color':'CornflowerBlue'})
        else:
            fig.update_traces(fill='tozeroy',line={'color':'CornflowerBlue'})
    elif day_end < day_start:
        fig.update_traces(fill='tozeroy',line={'color':'CornflowerBlue'})
    '''
    if day_end >= day_start:
        if day_end-day_start>=1.0:
            fig.update_traces(fill='tozeroy',line={'color':'IndianRed'})
        elif day_end-day_start>=0.2:
            fig.update_traces(fill='tozeroy',line={'color':'orange'})
        else:
            fig.update_traces(fill='tozeroy',line={'color':'green'})
    elif day_end < day_start:
        fig.update_traces(fill='tozeroy',line={'color':'CornflowerBlue'})
    '''

    return fig

# Pulling water level data from Hilltop Server
data = get_all_stage_data()
data["Time"] = pd.to_datetime(data["Time"],infer_datetime_format=True)
data["Value"] = pd.to_numeric(data["M1"])/1000.0
#data = data.query("SiteName == 'Makakahi at Hamua'")
# sites = list(np.sort(data.SiteName.unique()))

# Loading Sitename list, which will provide the subset of sites to plot
sites_df = pd.read_csv('SiteNames.csv')
#sites = list(np.sort(sites_df.SiteName.unique()))
sites = sites_df.query("FloodWarningSite == True")

# Loading site warning level reference data
warningLevels = pd.read_csv('sites-warning-status.csv')
Warnings = warningLevels.query("Source == 'Hilltop'")
warnings1 = Warnings.drop(columns=['StageDesc', 'StageValue','StageTime','SymbolRotation','HRCLat','HRCLong','HRCTMEasting','HRCTMNorthing','Field','TripLevelID','AlertType','Measurement'])

#Warnings = warningLevels.query("Source == 'RiverHeightsList'")
#warnings2 = Warnings.drop(columns=['StageDesc', 'StageValue','StageTime','SymbolRotation','HRCLat','HRCLong','HRCTMEasting','HRCTMNorthing','Field','TripLevelID','AlertType','Measurement'])

# Unique sites
sites = list(np.sort(warnings1.SiteName.unique()))
#sites2 = list(np.sort(warnings2.SiteName.unique()))



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
            build_card(0,sites)            
        ]),
        dbc.Col([
            build_card(1,sites)
        ]),
        dbc.Col([
            build_card(2,sites)
        ]),
        dbc.Col([
            build_card(3,sites)
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
            build_card(5,sites)
        ]),
        dbc.Col([
            build_card(6,sites)
        ]),
        dbc.Col([
            build_card(7,sites)
        ]),
    ],
    className="mb-4",
)

row_3 = dbc.Row(
    [
        dbc.Col([
            build_card(8,sites)            
        ]),
        dbc.Col([
            build_card(9,sites)
        ]),
        dbc.Col([
            build_card(10,sites)
        ]),
        dbc.Col([
            build_card(11,sites)
        ]),
    ],
    className="mb-4",
)

row_4 = dbc.Row(
    [
        dbc.Col([
            build_card(12,sites)            
        ]),
        dbc.Col([
            build_card(13,sites)
        ]),
        dbc.Col([
            build_card(14,sites)
        ]),
        dbc.Col([
            build_card(15,sites)
        ]),
    ],
    className="mb-4",
)

row_5 = dbc.Row(
    [
        dbc.Col([
            build_card(16,sites)            
        ]),
        dbc.Col([
            build_card(17,sites)
        ]),
        dbc.Col([
            # build_card(18,sites)
        ]),
        dbc.Col([
            # build_card(19,sites)
        ]),
    ],
    className="mb-4",
)

app.layout = dbc.Container([
    html.Div([row_1, row_2, row_3, row_4, row_5]),
    dcc.Interval(id='update', n_intervals=0, interval=1000*300)
])


@app.callback(
 [
    Output('indicator-graph-0','figure'),
    Output('indicator-graph-1','figure'),
    Output('indicator-graph-2','figure'),
    Output('indicator-graph-3','figure'),
    Output('indicator-graph-4','figure'),
    Output('indicator-graph-5','figure'),
    Output('indicator-graph-6','figure'),
    Output('indicator-graph-7','figure'),
    Output('indicator-graph-8','figure'),
    Output('indicator-graph-9','figure'),
    Output('indicator-graph-10','figure'),
    Output('indicator-graph-11','figure'),
    Output('indicator-graph-12','figure'),
    Output('indicator-graph-13','figure'),
    Output('indicator-graph-14','figure'),
    Output('indicator-graph-15','figure'),
    Output('indicator-graph-16','figure'),
    Output('indicator-graph-17','figure'),
    ],
    Input('update', 'n_intervals')
)

def update_graph(timer):
    # perform some logic here

    output_0 = build_card_indicator(0, sites, data)
    output_1 = build_card_indicator(1, sites, data)
    output_2 = build_card_indicator(2, sites, data)
    output_3 = build_card_indicator(3, sites, data)
    output_4 = build_card_indicator(4, sites, data)
    output_5 = build_card_indicator(5, sites, data)
    output_6 = build_card_indicator(6, sites, data)
    output_7 = build_card_indicator(7, sites, data)
    output_8 = build_card_indicator(8, sites, data)
    output_9 = build_card_indicator(9, sites, data)
    output_10 = build_card_indicator(10, sites, data)    
    output_11 = build_card_indicator(11, sites, data)
    output_12 = build_card_indicator(12, sites, data)
    output_13 = build_card_indicator(13, sites, data)
    output_14 = build_card_indicator(14, sites, data)
    output_15 = build_card_indicator(15, sites, data)
    output_16 = build_card_indicator(16, sites, data)
    output_17 = build_card_indicator(17, sites, data)
    
    return output_0, output_1, output_2, output_3, output_4, output_5, \
        output_6, output_7, output_8, output_9, output_10, output_11, \
        output_12, output_13, output_14, output_15, output_16, output_17

@app.callback(
    [
    Output('daily-line-0','figure'),
    Output('daily-line-1','figure'),
    Output('daily-line-2','figure'),
    Output('daily-line-3','figure'),
    Output('daily-line-4','figure'),
    Output('daily-line-5','figure'),
    Output('daily-line-6','figure'),
    Output('daily-line-7','figure'),
    Output('daily-line-8','figure'),
    Output('daily-line-9','figure'),
    Output('daily-line-10','figure'),
    Output('daily-line-11','figure'),
    Output('daily-line-12','figure'),
    Output('daily-line-13','figure'),
    Output('daily-line-14','figure'),
    Output('daily-line-15','figure'),
    Output('daily-line-16','figure'),
    Output('daily-line-17','figure'),
    ],
    Input('update', 'n_intervals')
)

# Line plot --------------------------------------------
def update_graph(timer):
    
    output_0 = build_card_graph(0, sites, data)
    output_1 = build_card_graph(1, sites, data)
    output_2 = build_card_graph(2, sites, data)
    output_3 = build_card_graph(3, sites, data)
    output_4 = build_card_graph(4, sites, data)
    output_5 = build_card_graph(5, sites, data)
    output_6 = build_card_graph(6, sites, data)
    output_7 = build_card_graph(7, sites, data)
    output_8 = build_card_graph(8, sites, data)
    output_9 = build_card_graph(9, sites, data)
    output_10 = build_card_graph(10, sites, data)    
    output_11 = build_card_graph(11, sites, data)
    output_12 = build_card_graph(12, sites, data)
    output_13 = build_card_graph(13, sites, data)
    output_14 = build_card_graph(14, sites, data)
    output_15 = build_card_graph(15, sites, data)
    output_16 = build_card_graph(16, sites, data)
    output_17 = build_card_graph(17, sites, data)
    
    return output_0, output_1, output_2, output_3, output_4, output_5, \
        output_6, output_7, output_8, output_9, output_10, output_11, \
        output_12, output_13, output_14, output_15, output_16, output_17
   

if __name__ == "__main__":
    app.run_server(debug=True)
