#_______________________________________________________________________________
#Import des packages

import pandas as pd
import plotly.graph_objects as go
from typing import Dict


#_______________________________________________________________________________
#Préparation des données

def prepare_pie_data(data: pd.DataFrame, country: str) -> Dict:
    """
    Prepare data for pie chart visualization
    
    Parameters:
    -----------
    data : pd.DataFrame
        The input dataframe containing test data
    country : str
        Selected country name
        
    Returns:
    --------
    Dict containing positive and negative test rates
    """
    # Filtrer les données pour le pays sélectionné
    df_filtered = data[data["COUNTRY_AREA_TERRITORY"] == country]
    
    if df_filtered.empty:
        return {"positive": 0, "negative": 0}
    
    # Agréger les données par semaine
    df_grouped = df_filtered.groupby("ISO_WEEKSTARTDATE").agg(
        total_tests=pd.NamedAgg(column="SPEC_PROCESSED_NB", aggfunc="sum"),
        total_positifs=pd.NamedAgg(column="INF_A", aggfunc="sum")
    ).reset_index()
    
    # Vérification pour éviter les divisions par zéro
    df_grouped["taux_positifs"] = df_grouped.apply(
        lambda row: (row["total_positifs"] / row["total_tests"]) * 100 
        if row["total_tests"] > 0 else 0, axis=1
    )
    df_grouped["taux_negatifs"] = 100 - df_grouped["taux_positifs"]
    
    # Moyenne sur toutes les semaines
    rates = {
        "positive": df_grouped["taux_positifs"].mean(),
        "negative": df_grouped["taux_negatifs"].mean()
    }
    
    return rates


#_______________________________________________________________________________
#Création du diagramme circulaire
def create_pie_chart(data: pd.DataFrame, country: str) -> go.Figure:
    """
    Create pie chart visualization for test rates
    
    Parameters:
    -----------
    data : pd.DataFrame
        The input dataframe containing test data
    country : str
        Selected country name
        
    Returns:
    --------
    plotly.graph_objects.Figure
        The pie chart figure
    """
    rates = prepare_pie_data(data, country)
    
    fig = go.Figure(data=[go.Pie(
        labels=["Positive (%)", "Negative (%)"],
        values=[rates["positive"], rates["negative"]],
        hole=0.3,
        marker_colors=["#FF4444", "#636EFA"],  # Custom colors for segments
        textinfo="percent",  # Display percentages
        textfont=dict(color="#CCCCCC", family="Oswald"),  # Change text color for better visibility
        pull=[0.1, 0]  # Slight pull on the positive slice to emphasize it
    )])
    
    # Update the layout for the pie chart itself and the background area
    fig.update_layout(
        plot_bgcolor="#292833",  # dark gray background for the plot area
        paper_bgcolor="#292833",  # dark background for the paper around the chart
        font=dict(color="#CCCCCC", family="Oswald"),  # Set font color to black for better visibility
        margin=dict(t=30, b=0, l=5, r=0),
        showlegend=True  # Show the legend
    )
    
    return fig
