"""
Module pour la visualisation de la carte
"""

import streamlit as st
import pydeck as pdk
import pandas as pd

def get_department_column(available_columns):
    """
    Détermine quelle colonne utiliser pour les départements selon les données disponibles
    """
    # Pour les conseillers régionaux, la colonne s'appelle "Libellé de la section départementale"
    if 'Libellé de la section départementale' in available_columns:
        return 'Libellé de la section départementale'
    # Pour les autres types d'élus
    elif 'Libellé du département' in available_columns:
        return 'Libellé du département'
    else:
        return None

def create_map(df: pd.DataFrame):
    """
    Crée une carte interactive des élus
    """
    try:
        # Vérifier les colonnes disponibles
        available_columns = df.columns.tolist()
        
        # Déterminer la colonne département appropriée
        dept_column = get_department_column(available_columns)
        
        # Colonnes de base nécessaires (adaptatives)
        base_columns = ['Latitude_Dept', 'Longitude_Dept', 'Nom de l\'élu', 'Prénom de l\'élu']
        if dept_column:
            base_columns.append(dept_column)
        
        # Vérifier que les colonnes de base existent
        missing_base = [col for col in base_columns if col not in available_columns]
        if missing_base:
            st.warning(f"Colonnes manquantes pour la carte : {missing_base}")
            return None
        
        # Colonnes optionnelles
        optional_columns = []
        if 'Libellé de la commune' in available_columns:
            optional_columns.extend(['Latitude_Commune', 'Longitude_Commune', 'Libellé de la commune'])
        if 'Libellé du canton' in available_columns:
            optional_columns.append('Libellé du canton')
        if 'Libellé de la fonction' in available_columns:
            optional_columns.append('Libellé de la fonction')
        
        # Sélectionner les colonnes disponibles pour la carte
        needed_columns = base_columns + optional_columns
        map_df = df[needed_columns].copy()
        
        # Permettre à l'utilisateur de choisir le type de visualisation
        viz_options = ["Agrégation hexagonale"]
        if 'Latitude_Commune' in available_columns and 'Longitude_Commune' in available_columns:
            viz_options.insert(0, "Points individuels")
        
        viz_type = st.radio(
            "Type de visualisation",
            viz_options,
            help="Choisissez entre des points individuels (si communes disponibles) ou une agrégation par zones"
        )
        
        # Filtrer les coordonnées invalides selon le type de visualisation
        if viz_type == "Points individuels" and 'Latitude_Commune' in map_df.columns:
            map_df = map_df[(map_df['Latitude_Commune'] != 0) & (map_df['Longitude_Commune'] != 0)]
        else:
            map_df = map_df[(map_df['Latitude_Dept'] != 0) & (map_df['Longitude_Dept'] != 0)]
        
        if map_df.empty:
            return None
        
        if viz_type == "Points individuels" and 'Latitude_Commune' in map_df.columns:
            # Si le dataframe est trop grand, prendre un échantillon
            if len(map_df) > 10000:
                map_df = map_df.sample(n=10000, random_state=42)
            
            # Utiliser les coordonnées des communes pour les points individuels
            map_df['position'] = map_df.apply(
                lambda row: [row['Longitude_Commune'], row['Latitude_Commune']], 
                axis=1
            )
            
            # Create a scatter plot layer
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=map_df,
                get_position='position',
                get_color=[200, 30, 0, 160],
                get_radius=50,
                pickable=True,
                auto_highlight=True,
                radius_scale=6,
                radius_min_pixels=3,
                radius_max_pixels=30,
                id="elected_officials"
            )
            
            # Create tooltip adaptatif
            tooltip_html = "<b>Nom:</b> {Prénom de l'élu} {Nom de l'élu}<br>"
            if 'Libellé de la commune' in map_df.columns:
                tooltip_html += "<b>Commune:</b> {Libellé de la commune}<br>"
            if 'Libellé du canton' in map_df.columns:
                tooltip_html += "<b>Canton:</b> {Libellé du canton}<br>"
            
            # Utiliser la colonne département appropriée
            if dept_column and dept_column in map_df.columns:
                if dept_column == 'Libellé de la section départementale':
                    tooltip_html += "<b>Section départementale:</b> {" + dept_column + "}"
                else:
                    tooltip_html += "<b>Département:</b> {" + dept_column + "}"
            
            if 'Libellé de la fonction' in map_df.columns:
                tooltip_html += "<br><b>Fonction:</b> {Libellé de la fonction}"
            
            tooltip = {
                "html": tooltip_html,
                "style": {
                    "backgroundColor": "steelblue",
                    "color": "white"
                }
            }
            
        else:  # Agrégation hexagonale
            # Utiliser les coordonnées des départements pour l'agrégation
            hex_df = pd.DataFrame({
                'position': map_df.apply(
                    lambda row: [row['Longitude_Dept'], row['Latitude_Dept']], 
                    axis=1
                )
            })
            
            # Configuration de la couche hexagonale
            layer = pdk.Layer(
                "HexagonLayer",
                data=hex_df,
                get_position='position',
                radius=10000,
                elevation_scale=50,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
                coverage=1,
                auto_highlight=True,
                colorRange=[
                    [65, 182, 196],
                    [127, 205, 187],
                    [199, 233, 180],
                    [237, 248, 177],
                    [255, 255, 204]
                ],
                id="hex_layer",
            )
            
            # Tooltip pour les hexagones
            tooltip = {
                "html": "<b>Nombre d'élus dans la zone:</b> {elevationValue}",
                "style": {
                    "backgroundColor": "steelblue",
                    "color": "white"
                }
            }

        # Configuration de la vue initiale
        view_state = pdk.ViewState(
            latitude=46.603354,  # Centre de la France
            longitude=1.888334,
            zoom=5.5,  # Zoom initial ajusté
            min_zoom=4,  # Zoom minimum pour voir la France entière
            max_zoom=15,  # Zoom maximum pour le détail
            pitch=45 if viz_type == "Agrégation hexagonale" else 0,
            bearing=0
        )
        
        # Créer la carte
        deck = pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=view_state,
            layers=[layer],
            tooltip=tooltip
        )
        
        return deck
    
    except Exception as e:
        st.error(f"Erreur lors de la création de la carte: {str(e)}")
        return None

def display_map(df: pd.DataFrame):
    """
    Affiche la carte dans l'application
    """
    st.header("Carte des Élus")
    st.caption("Note: Les coordonnées sont approximatives basées sur les départements")
    deck = create_map(df)
    if deck:
        st.pydeck_chart(deck, use_container_width=True)
    else:
        st.warning("Données de localisation non disponibles pour la carte.") 