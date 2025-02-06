#_______________________________________________________________________________
#Import des packages

import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
from typing import Dict, List
from datetime import datetime


#_______________________________________________________________________________
#Variable

current_year = datetime.now().year


#_______________________________________________________________________________
#Préparation des données

def load_and_prepare_data(
    data_path: str,
    geojson_path: str,
    disease_columns: List[str] = None
) -> tuple:
    """
    Load and prepare data for visualization
    """
    try:
        # Load the data
        data = pd.read_csv(data_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"The data file at {data_path} could not be found.")
    
    if disease_columns is None:
        disease_columns = [
            'INF_A', 'INF_B', 'ADENO', 'BOCA', 'HUMAN_CORONA',
            'METAPNEUMO', 'PARAINFLUENZA', 'RHINO', 'RSV'
        ]
    
    try:
        # Load the GeoJSON map
        with open(geojson_path) as f:
            geojson = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"The GeoJSON file at {geojson_path} could not be found.")
    
    # Melt the data
    melted_data = pd.melt(
        data,
        id_vars=['COUNTRY_CODE', 'COUNTRY_AREA_TERRITORY', 'ISO_YEAR', 'ISO_WEEK'],
        value_vars=disease_columns,
        var_name='DISEASE_TYPE',
        value_name='CASES'
    )
    
    # Data cleaning: fill NA cases and convert to numeric
    melted_data['CASES'] = pd.to_numeric(melted_data['CASES'].fillna(0), errors='coerce')
    
    # Extraire l'année à partir de ISO_YEAR (les 4 premiers chiffres)
    melted_data['YEAR'] = melted_data['ISO_YEAR'].astype(str).str[:4].astype(int)
    
    # Filtrer les données pour l'année actuelle (2025 par exemple)
    melted_data = melted_data[melted_data['YEAR'] == current_year]
    
    return melted_data, geojson, disease_columns

#_______________________________________________________________________________
#Création de la carte intéractive

def create_choropleth_map(
    melted_data: pd.DataFrame,
    geojson: Dict,
    disease_columns: List[str],
    color_scale: str = "Reds"
) -> go.Figure:
    """
    Create an interactive choropleth map with disease data
    """
    # Aggregate data for plotting
    aggregated_data = melted_data.groupby(
        ['COUNTRY_CODE', 'DISEASE_TYPE', 'COUNTRY_AREA_TERRITORY', 'YEAR']
    )['CASES'].sum().reset_index()

    # Create a choropleth map using Plotly
    fig = px.choropleth(
        aggregated_data,
        geojson=geojson,
        locations='COUNTRY_CODE',
        color='CASES',
        hover_name='COUNTRY_AREA_TERRITORY',
        animation_frame='DISEASE_TYPE',
        color_continuous_scale=color_scale,
        range_color=(0, aggregated_data['CASES'].quantile(0.95)),
        labels={'CASES': 'Number of Cases'},
        title=f"Cases Distribution in {current_year}"
    )
    
    # Update map layout and appearance
    fig.update_geos(
        showcountries=True,
        countrycolor="lightgray",  # Légère nuance de gris pour les pays
        showcoastlines=True,
        coastlinecolor="lightgray",  # Légère nuance de gris pour les côtes
        showframe=False,
        showland=True,
        landcolor="whitesmoke",  # Fond des terres légèrement gris
        bgcolor='#292833'  # Fond général de la carte en noir
    )
    
    fig.update_layout(
        height=800,
        margin={"r":0,"t":50,"l":0,"b":0},
        title_x=0.5,
        title_y=0.95,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            center=dict(lon=0, lat=20),
            projection_scale=1.2
        ),
        paper_bgcolor="#292833",  # Fond général 
        font=dict(color="#CCCCCC", family="Oswald", weight="bold")  # Texte sombre pour contraster avec le fond blanc
    )
    
    # Hover functionality for detailed information
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
        "Year: %{customdata[0]}<br>" +
        "Disease: %{animation_frame}<br>" +
        "Cases: %{z:,.0f}<br>" +
        "<extra></extra>",
        customdata=aggregated_data[['YEAR']].values
    )
    
    return fig