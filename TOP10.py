#_______________________________________________________________________________
#Import des packages

import pandas as pd
from dash import html
from datetime import datetime, date


#_______________________________________________________________________________
#Préparation des données

# Load data
file_path = "data_flunet.csv"
df = pd.read_csv(file_path)

# Define flu columns
flu_columns = ['AH1', 'AH1N12009', 'AH3', 'ANOTSUBTYPED', 'INF_A', 'INF_B', 'BYAM',
               'BVIC_2DEL', 'BVIC_3DEL', 'BVIC_NODEL', 'BVIC_DELUNK']

# Convert 'ISO_YEAR' to numeric and filter by current year
current_year = datetime.now().year
df['ISO_YEAR'] = pd.to_numeric(df['ISO_YEAR'], errors='coerce')
df = df[df['ISO_YEAR'] == current_year]

# Calculate total flu cases per country
df['TOTAL_FLU_CASES'] = df[flu_columns].sum(axis=1)
total_cases_by_country = df.groupby('COUNTRY_AREA_TERRITORY')['TOTAL_FLU_CASES'].sum().reset_index()

# Sort and get top 10
top_10_countries = total_cases_by_country.sort_values(by='TOTAL_FLU_CASES', ascending=False).head(10)
total_cases = int(total_cases_by_country['TOTAL_FLU_CASES'].sum())


#_______________________________________________________________________________
#Création du Top 10

def get_top10_component():
    return html.Div(
        id="toptotal",
        className="top-total-container",
        children=[
            # Header section
            html.Div(
                className="top-total-header",
                children=[
                    html.H3("Total Reported", className="total-title"),
                    html.H3("of " + str(date.today().year), className="total-titre"),
                    html.H2(f"{total_cases:,.0f}", className="total-number"),
                    html.H3("- Top 10 -", className="top-ten-title"),
                ]
            ),

            # List section
            html.Ul(
                className="top-countries-list",
                children=[
                    html.Li(
                        className="country-list-item",
                        children=html.Div(
                            className="country-item-content",
                            children=[
                                html.Span(
                                    row['COUNTRY_AREA_TERRITORY'],
                                    className="country-name"
                                ),
                                html.Span(
                                    f"{row['TOTAL_FLU_CASES']:,.0f}",
                                    className="country-value"
                                )
                            ]
                        )
                    )
                    for _, row in top_10_countries.iterrows()
                ]
            )
        ]
    )