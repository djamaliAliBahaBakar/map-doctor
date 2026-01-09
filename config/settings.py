# Paramètres de l'application
APP_TITLE = "Liste des professionnelles de santé de l'annuaire santé Ameli"
APP_DESCRIPTION = "Une application pour explorer et visualiser les données des professionnelles de santé d'Ameli "
APP_LAYOUT = "wide"
APP_INITIAL_SIDEBAR_STATE = "expanded"

# Définir le chemin des données
DATA_URL="https://static.data.gouv.fr/resources/annuaire-sante-ameli/20260105-014401/liste-ps-20260105-023058.csv"

# Chemins des fichiers de cache
DEPT_COORDS_CACHE = "dept_coords_cache.json"
COMMUNE_COORDS_CACHE = "commune_coords_cache.json"

# Colonnes importantes
COLONNES_PRINCIPALES = [
    'ps_activite_nom',
    'ps_activite_prenom',
    'coordonnees_ville'
]


# Paramètres de la carte
MAP_CENTER = [46.603354, 1.888334]  # Centre de la France
MAP_ZOOM = 6



DEFAULT_DEPT_COORDS = {
    "Ain": (46.0667, 5.3333),
    "Aisne": (49.5667, 3.6167),
    # ... (le reste des coordonnées)
} 