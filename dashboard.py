#_______________________________________________________________________________
#Import des packages

import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
import pandas as pd
import os
from datetime import datetime, date, timedelta
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html


#_______________________________________________________________________________
#Import des fonctions

from map import load_and_prepare_data, create_choropleth_map
from pie import create_pie_chart
from TOP10 import get_top10_component
from topweek import data_week, count_country, create_top10_bar
from line_chart import load_and_prepare_line_data, filter_line_data, create_line_chart


#_______________________________________________________________________________
#Définition des chemins

wd_csv="data_flunet.csv"
geojson_path =  "map.json"


#_______________________________________________________________________________
#Chargement du csv

data=pd.read_csv(wd_csv)


#_______________________________________________________________________________
#Camembert

default_country = data["COUNTRY_AREA_TERRITORY"].dropna().unique()[0]
initial_pie = create_pie_chart(data, default_country)


#_______________________________________________________________________________
#Top week

data_week=data_week(data)
sorted_data_week=data_week.sort_values(by="ISO_WEEKSTARTDATE", ascending=False)
last_date=list(sorted_data_week.ISO_WEEKSTARTDATE)[0]
last_date_minus_seven=str(datetime.strptime(last_date, "%Y-%m-%d")-timedelta(7))[:10]
fig_bar_init = create_top10_bar(data_week)


#_______________________________________________________________________________
#Carte

# Chargement et préparation des données pour la carte
melted_data, geojson, disease_columns = load_and_prepare_data(wd_csv, geojson_path)

# Création de la carte choroplèthe
choropleth_map = create_choropleth_map(melted_data, geojson, disease_columns)


#_______________________________________________________________________________
#Courbe

line_data, _, virus_columns = load_and_prepare_line_data(wd_csv)
data['ISO_DATE'] = pd.to_datetime(data['ISO_WEEKSTARTDATE'])


#_______________________________________________________________________________
# Layout de l'application Dash

app = dash.Dash(__name__)

external_style = ["/assets/style.css"]

app.layout = html.Div(id="dashboard", children=[
    html.Div(id="titre", children=[html.Div(id="titre-left", children=[
                                    html.Div([
                                        dbc.Button("How does it work ?", id="open", n_clicks=0, color="primary", className="btn"),
                                        dbc.Modal([
                                                html.H3("How does the dashboard work", id="modal-title"),
                                                dbc.ModalBody(children=[html.H4("VIRAL INFECTIONS TRACKER :", className="modal-section"),
                                                                            html.P("This interactive and up-to-date dashboard follows the course of different viruses around the world, thanks to several dynamic graphs that are offered.", className="modal-paragraph"),
                                                                            html.P("The data came from the World Health Organization's website.", className="modal-paragraph"),
                                                                        html.H4("Positive and negative tests rate of the current week :", className="modal-section"),
                                                                            html.P("This pie chart presents, by country, the distribution of positive and negative tests for the week. It is possible to select a country by clicking on the arrow.", className="modal-paragraph"),
                                                                        html.H4("Top 10 of the week - Number of infections :", className="modal-section"),
                                                                            html.P("This barplot presents the ten countries that have had the most infections in the last week. It is possible to select a different virus by clicking on the arrow. To see the number of cases for the week, the bar can be hovered over with the mouse.", className="modal-paragraph"),
                                                                        html.H4("Case distribution in " + str(date.today().year) + " :", className="modal-section"),
                                                                            html.P("This map shows the number of cases by country. The colour scale quickly shows the incidence: the redder the country, the higher its incidence.", className="modal-paragraph"),
                                                                            html.P("It is possible to select a different virus using the horizontal bar below the graph to vary the incidence: ADENO, BOCA, HUMAN_CORONA, INF_A, INF_B, METAPNEUMO, PARA_INFLUENZA, RHINO, RSV. A mouse can be used to hover over the countries in question and its impact.", className="modal-paragraph"),
                                                                        html.H4("Evolution of Respiratory Virus Cases :", className="modal-section"),
                                                                            html.P("This graphic represents the evolution of a virus over time for one or more given countries. For more readability, it is possible to zoom in on the graph.", className="modal-paragraph"),
                                                                            html.P("It is possible to select one or more regions of the world, one or more countries, as well as one or more viruses. To see the selected choices, it is possible to scroll inside the input fields, which will also remove the selected choices by clicking on the cross.", className="modal-paragraph"),
                                                                        html.H4("Total Reported of " + str(date.today().year) + " :", className="modal-section"),
                                                                            html.P("This Top 10 includes the total number of cases reported over the current year, as well as the countries most affected during the current year, all viruses combined. It is possible to scroll through the first countries indicated to see the rest of the ranking.", className="modal-paragraph")
                                                                    ]),
                                                dbc.ModalFooter(
                                                    dbc.Button(
                                                        "Close", id="close", className="ms-auto", n_clicks=0
                                                    ), id="footer"
                                                )],
                                            id="modal",
                                            is_open=False,
                                        ),
                                    ])]),
                                    html.Div(id="titre-center", children=[html.H1("Viral infections tracker")]),
                                    html.Div(id="titre-right", children=[html.A("> GitHub",
                                                    href="https://github.com/Eden-BETE/influenza_tracker",
                                                    target="_blank",
                                                )
    ])]),
    html.Div(id="left", children=[
        html.Div(id="camembert", children=[
            html.H3("Positive and Negative Tests Rate of the Current Week"),
            dcc.Dropdown(
                id="dropdown-country",
                options=[{"label": country, "value": country}
                        for country in sorted(data["COUNTRY_AREA_TERRITORY"].dropna().unique())],
                value="France",
                placeholder="Sélectionner un pays",
                style={
                    "color": "#1D1C22",
                    "backgroundColor": "#1D1C22"
                }
            ),
            dcc.Graph(id="graph-pie", figure=initial_pie)
        ]),
        html.Div(id="topweek", children=[
                                    dcc.Dropdown(id="virus-topweek",
                                        options=[
                                            {"label": "ADENO", "value" : "ADENO"},
                                            {"label": "BOCA", "value" : "BOCA"},
                                            {"label": "Human corona", "value" : "HUMAN_CORONA"},
                                            {"label": "Influenza A", "value" : "INF_A"},
                                            {"label": "Influenza - Total", "value" : "INF_ALL"},
                                            {"label": "Influenza B", "value" : "INF_B"},
                                            {"label": "Metapneumo", "value" : "METAPNEUMO"},
                                            {"label": "Parainfluenza", "value" : "PARAINFLUENZA"},
                                            {"label": "Rhino", "value" : "RHINO"},
                                            {"label": "RSV", "value" : "RSV"}
                                        ],
                                        value="INF_ALL"
                                    ),
                                    html.Div(id="titre-graphtopweek", children=[html.H4("Top 10 of the Week - Number of Infections")]),
                                    html.Div(id="title-graph-topweek", children=[html.H6(last_date_minus_seven + " - " + last_date)]),
                                    html.Div(id="graph-topweek", children=[fig_bar_init])
            ])
    ]),
    html.Div(id="center", children=[
        html.Div(id="carte", children=[dcc.Graph(id="graph-carte", figure=choropleth_map)]),
        html.Div(id="courbe", children=[
            html.H3("Evolution of Respiratory Virus Cases"),
            html.Div(id="div-line", children=[
                html.Div(id="input-line", children=[
                    dcc.Dropdown(
                        id='line-region-filter',
                        options=[{'label': region, 'value': region} for region in sorted(data['WHOREGION'].unique())],
                        value=["EUR"],
                        multi=True,
                        placeholder="Select Region(s)"
                    ),
                    dcc.Dropdown(
                        id='line-country-filter',
                        options=[{"label": country, "value": country}
                                for country in sorted(data["COUNTRY_AREA_TERRITORY"].dropna().unique())],
                        value="France",
                        multi=True,
                        placeholder="Select Country(ies)"
                    ),
                    dcc.Dropdown(
                        id='line-virus-filter',
                        options=[{'label': col, 'value': col} for col in virus_columns],
                        value=['INF_A'],
                        multi=True,
                        placeholder="Select Virus(es)"
                    ),
                ]),
                dcc.Graph(id='line-chart')
            ])
        ])
    ]),
    html.Div(id="right", children=[
        get_top10_component(),
        html.Div(id="source", children=[
                    html.P(["Last update : ", str(date.today())]),
                    html.P(["Data source : ", html.A("FluNet", href='https://app.powerbi.com/view?r=eyJrIjoiNjViM2Y4NjktMjJmMC00Y2NjLWFmOWQtODQ0NjZkNWM1YzNmIiwidCI6ImY2MTBjMGI3LWJkMjQtNGIzOS04MTBiLTNkYzI4MGFmYjU5MCIsImMiOjh9',     target="_blank")]),
                    html.P(["Created by : ", html.A("AGODE M.", href='https://moise-agode.github.io/', target="_blank"), ", ",
                            html.A("BETE E.", href='https://eden-bete.github.io/portfolio/', target="_blank"), ", ",
                            html.A("DENIS T.", href='https://www.theo-denis.com/Portfolio%20-%20English.html', target="_blank"), ", ",
                            html.A("MIEMO B.", href='https://borgiamiemo.github.io/Portfolio/', target="_blank"), ", ",
                            html.A("SORO C.", href='https://christelle-soro.github.io/portfolio/', target="_blank")])
        ])
    ])
])


#Mise à jour du graphique topweek
@app.callback(
    Output(component_id="graph-topweek", component_property="children"),
    [Input(component_id="virus-topweek", component_property="value")]
)

def update_graph(selected_virus):
    return create_top10_bar(data_week, selected_virus)


#Mise à jour du pie-chart
@app.callback(
    Output("graph-pie", "figure"),
    [Input("dropdown-country", "value")]
)
def update_pie_chart(selected_country):
    return create_pie_chart(data, selected_country)


#Mise à jour de la courbe
@app.callback(
    [Output('line-country-filter', 'options'),
     Output('line-country-filter', 'value')],
    [Input('line-region-filter', 'value')]
)
def update_line_country_options(selected_region):
    if not selected_region:
        return [], None
    filtered_countries = sorted(data[data['WHOREGION'].isin(selected_region)]['COUNTRY_AREA_TERRITORY'].unique())
    options = [{'label': country, 'value': country} for country in filtered_countries]
    return options, [options[0]['value']] if options else None


# Mise à jour du graphique de courbe en fonction des filtres
@app.callback(
    Output('line-chart', 'figure'),
    [Input('line-region-filter', 'value'),
     Input('line-country-filter', 'value'),
     Input('line-virus-filter', 'value')]
)
def update_line_chart(selected_region, selected_country, selected_virus):
    if not all([selected_region, selected_country, selected_virus]):
        return {}  # Return empty figure if any input is missing
    filtered_data = filter_line_data(line_data, selected_region, selected_country, selected_virus)
    return create_line_chart(filtered_data, selected_virus)


#Modal
@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

#_______________________________________________________________________________

if __name__ == "__main__" :
    app.run_server(debug=False)