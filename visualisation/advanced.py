"""
Module de visualisations avancées
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from typing import Optional



def create_specialite_analysis(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Analyse des specialités les plus représentées
    """

    if 'specialite_libelle' not in df.columns:
        return None

    # Get specialite counts
    specialite_counts = df['specialite_libelle'].value_counts().head(15)
    
    # Create bar chart
    fig = px.bar(
        x=specialite_counts.index,
        y=specialite_counts.values,
        labels={'x': 'Specialité', 'y': 'Nombre de specialistes'},
        title="Spécialités les plus représentées",
        color=specialite_counts.values,
        color_continuous_scale='Viridis'
    )
    
    # Update layout for readability
    fig.update_layout(
        xaxis={'categoryorder':'total descending'},
        xaxis_tickangle=-45
    )
    
    return fig

def plot_gender_distribution(df: pd.DataFrame):
    """
    Crée un graphique circulaire de la répartition par genre
    """
    gender_col = 'ps_activite_civilite' if 'ps_activite_civilite' in df.columns else None
    if not gender_col:
        return None
    
    gender_counts = df[gender_col].value_counts()
    fig = px.pie(
        values=gender_counts.values,
        names=gender_counts.index,
        title="Répartition par Genre",
        color_discrete_sequence=px.colors.sequential.Viridis,
        hole=0.4
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig


def plot_specialite_by_ville(df: pd.DataFrame):
    """
    Crée un graphique en barres de medecins par ville
    """
    # Détecter la colonne appropriée
    ville_col = None
    title_text = "Nombre de médecins par ville (Top 20)"
    x_label = "Ville"
    
    if 'coordonnees_ville' in df.columns:
        ville_col = 'coordonnees_ville'
        title_text = "Nombre de médecins par ville (Top 20)"
        x_label = "Ville"



    if not ville_col:
        return None

    ville_counts = df[ville_col].value_counts().nlargest(20)
    fig = px.bar(
        x=ville_counts.index,
        y=ville_counts.values,
        title=title_text,
        labels={'x': x_label, 'y': "Nombre de spécialistes"},
        color=ville_counts.values,
        color_continuous_scale=px.colors.sequential.Viridis
    )
    return fig



def display_advanced_visualizations(df: pd.DataFrame):
    """
    Affiche toutes les visualisations avancées
    """
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution par genre
        gender_fig = plot_gender_distribution(df)
        if gender_fig:
            st.plotly_chart(gender_fig, use_container_width=True)
        else:
            st.warning("Données de genre non disponibles pour la visualisation.")
        
    
    with col2:
        # specialité par ville
        dept_fig = plot_specialite_by_ville(df)
        if dept_fig:
            st.plotly_chart(dept_fig, use_container_width=True)
        else:
            st.warning("Données de ville non disponibles pour la visualisation.")

    st.header("Analyses Avancées")
    
    # Create tabs for different visualizations
    tabs = st.tabs([
        "Specialités"
    ])
    
    with tabs[0]:   
        st.subheader("Analyse des spécialités les plus représentées")
        specialite_chart = create_specialite_analysis(df)
        if specialite_chart:
            st.plotly_chart(specialite_chart, use_container_width=True)
        else:
            st.warning("Données de spécialité non disponibles pour cette visualisation.")

