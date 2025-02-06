#_______________________________________________________________________________
#Import des packages

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os


#_______________________________________________________________________________
#Préparation des donneés

def load_and_prepare_line_data(wd_csv):
    # Load data from CSV
    data = pd.read_csv(wd_csv)
    
    # Convert ISO_WEEKSTARTDATE to datetime
    data['ISO_DATE'] = pd.to_datetime(data['ISO_WEEKSTARTDATE'])
    
    # Define virus columns
    virus_columns = [
        'ADENO', 'BOCA', 'HUMAN_CORONA', 'INF_A', 'INF_B', 
        'METAPNEUMO', 'PARAINFLUENZA', 'RHINO', 'RSV'
    ]
    
    # Keep only necessary columns
    columns_to_keep = ['ISO_DATE', 'COUNTRY_AREA_TERRITORY', 'WHOREGION'] + virus_columns
    data = data[columns_to_keep]
    
    # Fill NaN values with 0
    data[virus_columns] = data[virus_columns].fillna(0)
    
    return data, columns_to_keep, virus_columns
    
    
#_______________________________________________________________________________
#Filtrage des données

def filter_line_data(data, selected_region, selected_country, selected_virus):
    filtered_data = data.copy()
    start_date=list(pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_flunet.csv")).sort_values(by="ISO_WEEKSTARTDATE", ascending=False).ISO_WEEKSTARTDATE)[-1]
    end_date=list(pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_flunet.csv")).sort_values(by="ISO_WEEKSTARTDATE", ascending=False).ISO_WEEKSTARTDATE)[0]
    
    # Convert string dates to datetime if they aren't already
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)
    
    # Apply filters
    if selected_region:
        filtered_data = filtered_data[filtered_data['WHOREGION'].isin(selected_region)]
    
    if selected_country:
        filtered_data = filtered_data[filtered_data['COUNTRY_AREA_TERRITORY'].isin(selected_country)]
    
    # Filter by date range
    filtered_data = filtered_data[
        (filtered_data['ISO_DATE'] >= start_date) & 
        (filtered_data['ISO_DATE'] <= end_date)
    ]
    
    # Group by date and aggregate virus cases
    if selected_country:
        grouped_data = filtered_data.groupby(['ISO_DATE', 'COUNTRY_AREA_TERRITORY'])[selected_virus].sum().reset_index()
    else:
        grouped_data = filtered_data.groupby(['ISO_DATE'])[selected_virus].sum().reset_index()
    
    return grouped_data
    

#_______________________________________________________________________________
#Création du graphique

def create_line_chart(filtered_data, selected_virus):
    fig = go.Figure()
    
    # Add traces for each country if multiple countries are selected
    if 'COUNTRY_AREA_TERRITORY' in filtered_data.columns:
        for country in filtered_data['COUNTRY_AREA_TERRITORY'].unique():
            country_data = filtered_data[filtered_data['COUNTRY_AREA_TERRITORY'] == country]
            for virus in selected_virus:
                fig.add_trace(go.Scatter(
                    x=country_data['ISO_DATE'],
                    y=country_data[virus],
                    mode='lines+markers',
                    name=f'{virus} - {country}',
                    line=dict(width=2),
                    marker=dict(size=5)
                ))
    else:
        # Single trace for each virus if no country filter
        for virus in selected_virus:
            fig.add_trace(go.Scatter(
                x=filtered_data['ISO_DATE'],
                y=filtered_data[virus],
                mode='lines+markers',
                name=virus,
                line=dict(width=2),
                marker=dict(size=5),
                plot_bgcolor="#292833",
                paper_bgcolor="#292833",
                font=dict(color="#CCCCCC", family="Oswald"),
            ))
    
    # Update layout
    fig.update_layout(
        yaxis_title="Number of Cases",
        plot_bgcolor="#292833",
        paper_bgcolor="#292833",
        font=dict(color="#CCCCCC", family="Oswald"),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    return fig