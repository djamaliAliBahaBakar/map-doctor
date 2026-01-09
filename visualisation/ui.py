import streamlit as st
import pandas as pd
from config.settings import APP_TITLE, APP_DESCRIPTION,  APP_LAYOUT, APP_INITIAL_SIDEBAR_STATE


def setup_page(title: str = APP_TITLE, description: str = APP_DESCRIPTION):
    """Configure la page Streamlit"""
    st.set_page_config(
        page_title=title,
       # page_icon=APP_ICON,
        layout=APP_LAYOUT,
        initial_sidebar_state=APP_INITIAL_SIDEBAR_STATE
    )

def display_data_preview(df: pd.DataFrame, colonnes: list):
    """Affiche un aperçu des données"""
    with st.expander("Informations sur les données"):
        st.write("Colonnes disponibles dans le jeu de données:")
        st.write(df.columns.tolist())
        st.write("Aperçu des premières lignes:")
        st.dataframe(df[colonnes].head(3))

def download_button(df: pd.DataFrame):
    """Ajoute un bouton de téléchargement pour les données"""
    csv = df.to_csv(index=False)
    st.download_button(
        label="Télécharger les données complètes (CSV)",
        data=csv,
        file_name="repertoire_des_elus_filtré.csv",
        mime="text/csv"
    )

def display_stats(df: pd.DataFrame):
    """Affiche les statistiques dans la barre latérale"""
    st.sidebar.header("Statistiques")
    st.sidebar.metric("Nombre total de médecins", len(df))
    
    if 'ps_activite_civilite' in df.columns:
        gender_ratio = df['ps_activite_civilite'].value_counts(normalize=True).to_dict()
        male_pct = gender_ratio.get('M', 0) * 100
        female_pct = gender_ratio.get('F', 0) * 100
        st.sidebar.metric("Pourcentage d'hommes", f"{male_pct:.1f}%")
        st.sidebar.metric("Pourcentage de femmes", f"{female_pct:.1f}%")

def display_filters(df: pd.DataFrame):
    """Affiche les filtres dans la barre latérale adaptés au type de données"""
    st.sidebar.header("Filtres")

    # Filtre par Ville (adaptatif)
    selected_villes = []
    dept_label = "Ville"
    
    # Détecter la colonne ville appropriée
   
    if 'coordonnees_ville' in df.columns:
        villes = df['coordonnees_ville'].dropna().astype(str).unique()
        all_villes = sorted(villes)
        selected_villes = st.sidebar.multiselect(
            dept_label,
            options=all_villes,
            default=[]
        )
    
    # Filtre par genre (toujours présent)
    selected_gender = "Tous"
    if 'ps_activite_civilite' in df.columns:
        genders = df['ps_activite_civilite'].dropna().unique()
        gender_options = ["Tous"] + sorted(genders.tolist())
        selected_gender = st.sidebar.radio(
            "Genre",
            options=gender_options
        )

    # Filtre de recherche textuelle
    search_term = st.sidebar.text_input(
        "Rechercher un médecin ou une ville",
        help="Recherche dans les noms, prénoms, ville"
    )
    
    return {
        'villes' : selected_villes, 
        'gender': selected_gender, 
        'search_term' : search_term
    }
    


def display_about():
    """Affiche la section À propos"""
    st.markdown("""
    Cette application permet d'explorer les médecins dans le territoire français.
    Elle offre des fonctionnalités de filtrage, de visualisation et d'analyse
    de données.
    
    ### Source des données
    Les données proviennent du site [data.gouv.fr](https://www.data.gouv.fr/organizations/caisse-nationale-de-lassurance-maladie),
    qui est la plateforme de données ouvertes du gouvernement français.
    
    ### Fonctionnalités
    - Filtrage par ville, genre et recherche textuelle
    - Visualisation de la répartition par genre
    - Carte interactive des médecins
    - Tableau interactif des résultats filtrés
    
    ### Développé avec
    - [Streamlit](https://streamlit.io/) - Framework pour applications de données
    - [Pandas](https://pandas.pydata.org/) - Manipulation de données
    - [Plotly](https://plotly.com/) - Visualisations interactives
    - [PyDeck](https://deckgl.readthedocs.io/) - Cartographie interactive
    """)