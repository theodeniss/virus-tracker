#_______________________________________________________________________________
#Import des packages

import plotly.graph_objects as go
import pandas as pd
import os
from datetime import datetime, date, timedelta
from dash import dcc
from dash import html


#_______________________________________________________________________________
#Filtrages des données des sept derniers jours à compter de la date du dernier enregistrement

def data_week (data):
    sorted_df=data.sort_values(by="ISO_WEEKSTARTDATE", ascending=False)
    last_date=list(sorted_df.ISO_WEEKSTARTDATE)[0]
    filtered_df = data[data["ISO_WEEKSTARTDATE"] > str(datetime.strptime(last_date, "%Y-%m-%d")-timedelta(7))]
    return filtered_df


#_______________________________________________________________________________
#Compter les cas par pays et prendre le top 10

def count_country(df, value="INF_ALL"):
    grouped = df.groupby('COUNTRY_AREA_TERRITORY')[value].sum().reset_index()
    countries=list(grouped.COUNTRY_AREA_TERRITORY)
    count=list(grouped[value])
    countries=list(reversed(list(reversed([i for _, i in sorted(zip(count, countries))]))[:10]))
    count=list(reversed(list(reversed(sorted(count)))[:10]))
    return countries, count


#_______________________________________________________________________________
#Création du graphique

def create_top10_bar(data_week, virus="INF_ALL"):
    countries, count = count_country(data_week, virus)

    fig_bar = dcc.Graph(
        id="graph-topweek2",
        figure={
            "data": [
                {
                    "x": count,
                    "y": countries,
                    "type": "bar",
                    "orientation": "h",
                    "marker": {
                        "color": "#FF4444"
                    }
                }
            ],
            "layout": {
                "plot_bgcolor": "#292833",
                "paper_bgcolor": "#292833",
                "xaxis": {
                    "tickfont": {"color": "#CCCCCC", "family":"Oswald"},
                    "showgrid": False,
                    "gridcolor": "#404040",
                },
                "yaxis": {
                    "tickfont": {
                        "color": "#fff",
                        "size": 10,
                        "family":"Oswald"
                    },
                },
                "margin": {
                    "r": 0,
                    "t": 10,
                    "b": 0
                },
                "height": 250,
                "barmode": "stack",
            }
        }
    )
    return fig_bar
