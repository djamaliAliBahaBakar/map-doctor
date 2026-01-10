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
            df = pd.read_csv(StringIO(content), encoding='utf-8', sep=';', on_bad_lines='skip', low_memory=False)
            st.success(f"✅ {len(df)} enregistrements chargés depuis l'URL")           
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
        # Lire le fichier CSV
        df = pd.read_csv(cache_file, encoding='utf8',sep=';')
        # Creer le dictionnaire {code postale : {lat,lon)}}
        coords_dict = {}
        for _, row in df.iterrows():
            coords_dict[row['code_postal']] = (row['lon'], row['lat'])
        st.success(f"✅ {len(df)} communes chargées depuis {cache_file}")
        return coords_dict
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
    if filters.get('specialite') and 'specialite_libelle' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['specialite_libelle'].fillna('').astype(str) == filters['specialite']]
    
    
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
def preprocess_data(data: pd.DataFrame, ville_cache: dict) -> pd.DataFrame:
    """
    Prétraite les données avec mise en cache Streamlit
    """
    if data.empty:
        #print("Les données sont vides, aucun prétraitement effectué.")
        return data
    
    # Ajouter les coordonnées des villes (seulement si la colonne existe)
    is_coordonnees_code_postal = 'coordonnees_code_postal' in data.columns
    if is_coordonnees_code_postal:
        def get_coordinates(code_postal):
            if pd.isna(code_postal):
                return None, None
            
            key = str(int(code_postal))
            
            # Cherche dans le cache
            coords = ville_cache.get(key, (None, None))
            return coords[0], coords[1]  # (latitude, longitude)
        coordinates = data['coordonnees_code_postal'].apply(get_coordinates)
        data['Latitude_Ville'] = coordinates.apply(lambda x: x[0])
        data['Longitude_Ville'] = coordinates.apply(lambda x: x[1])
      
    else:
        # Si pas de code postal ville, initialiser les colonnes avec des valeurs nulles
        data['Latitude_Ville'] = None
        data['Longitude_Ville'] = None
    
    
    return data 