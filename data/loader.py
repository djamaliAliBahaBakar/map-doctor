import pandas as pd
import numpy as np
import json
import requests
from io import StringIO
import streamlit as st
from config.settings import DATA_URL, DEFAULT_DEPT_COORDS


@st.cache_data(ttl=86400)  # Cache pendant 24 heures
def load_data() -> pd.DataFrame:
    """
    Charge les données depuis l'URL avec mise en cache Streamlit
    """
        
    try:
        with st.spinner("Chargement des données..."):
            response = requests.get(DATA_URL)
            response.raise_for_status()  # Lever une exception en cas d'erreur HTTP
            
            # Lire le contenu CSV avec l'encodage approprié
            content = response.content.decode('utf-8', errors='replace')
            df = pd.read_csv(StringIO(content), sep=";", low_memory=False)
           
            return df
        
    except requests.exceptions.Timeout:
        st.error("⏱️ Délai d'attente dépassé")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Erreur HTTP : {e}")
    except Exception as e:
        st.error(f"❌ Erreur : {str(e)}")
        return pd.DataFrame()
    
@st.cache_data(ttl=86400)  # Cache pendant 24 heures
def load_coords_cache(cache_file: str) -> dict:
    '''
    Charge les coordonnées depuis le fichier de cache avec mise en cache Streamlit
    '''
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Erreur lors du chargement du cache {cache_file} : {str(e)}")
        if 'dept' in cache_file.lower():
            return DEFAULT_DEPT_COORDS
        return {}
    
def filter_data(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Filtre les données selon les critères sélectionnés
    """
    filtered_df = df.copy()
    
    # Filtre par nom (adaptatif)
    if filters.get('nom') and 'ps_activite_nom' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['ps_activite_nom'].fillna('').astype(str) == filters['nom']]
    
    # Filtre par prenom (adaptatif)
    if filters.get('prenom') and 'ps_activite_prenom' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['ps_activite_prenom'].fillna('').astype(str) == filters['prenom']]
    
    # Filtre par genre / ps_activite_civilite
    if filters.get('genre') and filters['genre'] != "Tous" and 'ps_activite_civilite' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['ps_activite_civilite'].fillna('').astype(str) == filters['genre']]

    # Filtre par ville / coordonnees_ville
    if filters.get('ville') and 'coordonnees_ville' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['coordonnees_ville'].fillna('').astype(str) == filters['ville']]

    # Filtre par code postale / coordonnees_code_postal
    if filters.get('code_postal') and 'coordonnees_code_postal' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['coordonnees_code_postal'].fillna('').astype(str) == filters['code_postal']]

    # Filtre par specialité / type_ps_libelle
    if filters.get('specialite') and 'type_ps_libelle' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['type_ps_libelle'].fillna('').astype(str) == filters['specialite']]
    
    
    # Filtre par terme de recherche
    search_term = filters.get('search_term', '')
    if search_term:
        search_conditions = []
        
        # Recherche dans les noms et prénoms
        if 'ps_activite_nom' in filtered_df.columns:
            search_conditions.append(filtered_df['ps_activite_nom'].fillna('').astype(str).str.contains(search_term, case=False, na=False))
        if 'ps_activite_prenom' in filtered_df.columns:
            search_conditions.append(filtered_df['ps_activite_prenom'].fillna('').astype(str).str.contains(search_term, case=False, na=False))
        
        # Recherche dans les villes
        if 'coordonnees_ville' in filtered_df.columns:
            search_conditions.append(filtered_df['coordonnees_ville'].fillna('').astype(str).str.contains(search_term, case=False, na=False))
        
        # Recherche dans codes postaux
        if 'coordonnees_code_postal' in filtered_df.columns:
            search_conditions.append(filtered_df['coordonnees_code_postal'].fillna('').astype(str).str.contains(search_term, case=False, na=False))
          
        if search_conditions:
            search_condition = search_conditions[0]
            for cond in search_conditions[1:]:
                search_condition = search_condition | cond
            filtered_df = filtered_df[search_condition]
    
    return filtered_df

@st.cache_data
def preprocess_data(data: pd.DataFrame, commune_cache: dict, dept_cache: dict) -> pd.DataFrame:
    """
    Prétraite les données avec mise en cache Streamlit
    """
    if data.empty:
        return data
    
    # Ajouter les coordonnées des communes (seulement si la colonne existe)
    if 'Libellé de la commune' in data.columns:
        data['Latitude_Commune'] = data['Libellé de la commune'].map(lambda x: commune_cache.get(str(x), (None, None))[0] if pd.notna(x) else None)
        data['Longitude_Commune'] = data['Libellé de la commune'].map(lambda x: commune_cache.get(str(x), (None, None))[1] if pd.notna(x) else None)
    else:
        # Si pas de communes, initialiser les colonnes avec des valeurs nulles
        data['Latitude_Commune'] = None
        data['Longitude_Commune'] = None
    
    # Ajouter les coordonnées des départements (adaptatif selon le type de données)
    dept_column = None
    if 'Libellé de la section départementale' in data.columns:
        dept_column = 'Libellé de la section départementale'
    elif 'Libellé du département' in data.columns:
        dept_column = 'Libellé du département'
    
    if dept_column:
        data['Latitude_Dept'] = data[dept_column].map(lambda x: dept_cache.get(x, (None, None))[0] if pd.notna(x) else None)
        data['Longitude_Dept'] = data[dept_column].map(lambda x: dept_cache.get(x, (None, None))[1] if pd.notna(x) else None)
    else:
        # Si pas de départements, initialiser les colonnes avec des valeurs nulles
        data['Latitude_Dept'] = None
        data['Longitude_Dept'] = None
    
    # Ajouter un décalage aléatoire pour les coordonnées (seulement si elles existent)
    if 'Latitude_Dept' in data.columns and 'Longitude_Dept' in data.columns:
        # Vérifier qu'il y a des valeurs non nulles avant d'ajouter le décalage
        mask_dept = data['Latitude_Dept'].notna() & data['Longitude_Dept'].notna()
        if mask_dept.any():
            data.loc[mask_dept, 'Latitude_Dept'] = data.loc[mask_dept, 'Latitude_Dept'] + np.random.normal(0, 0.05, size=mask_dept.sum())
            data.loc[mask_dept, 'Longitude_Dept'] = data.loc[mask_dept, 'Longitude_Dept'] + np.random.normal(0, 0.05, size=mask_dept.sum())
    
    if 'Latitude_Commune' in data.columns and 'Longitude_Commune' in data.columns:
        # Vérifier qu'il y a des valeurs non nulles avant d'ajouter le décalage
        mask_commune = data['Latitude_Commune'].notna() & data['Longitude_Commune'].notna()
        if mask_commune.any():
            data.loc[mask_commune, 'Latitude_Commune'] = data.loc[mask_commune, 'Latitude_Commune'] + np.random.normal(0, 0.001, size=mask_commune.sum())
            data.loc[mask_commune, 'Longitude_Commune'] = data.loc[mask_commune, 'Longitude_Commune'] + np.random.normal(0, 0.001, size=mask_commune.sum())
    
    # Remplacer les valeurs manquantes par 0 pour les coordonnées
    coord_cols = ['Latitude_Dept', 'Longitude_Dept', 'Latitude_Commune', 'Longitude_Commune']
    for col in coord_cols:
        if col in data.columns:
            data[col] = data[col].fillna(0)
    
    return data 