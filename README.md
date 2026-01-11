# Explorateur du Répertoire des médecins 
Une application Streamlit interactive pour explorer et visualiser les données des médecins du territoire français

## 🛠️ Installation

1.Clonez le repository :

```git clone <repository-url>
cd map-doctor
```

2.Installez les dépendances :

`pip install -r requirements.txt`

3.Lancez l'application :

`streamlit run app.py`

## 📊 Sources de données

Les données proviennent du site officiel data.gouv.fr 

## 🏗️ Architecture

```├── app.py                 # Application principale
├── config/
│   └── settings.py       # Configuration des types demédecis et URLs
├── data/
│   └── loader.py         # Chargement et filtrage des données
├── visualization/
│   ├── ui.py            # Composants d'interface utilisateur
│   ├── map.py           # Carte interactive
│   └── advanced.py      # Visualisations avancées
└── utils/               # Utilitaires
```


## 🔧 Technologies utilisées

- Streamlit - Framework d'application web
- Pandas - Manipulation de données
- Plotly - Visualisations interactives
- PyDeck - Cartographie 3D
- Requests - Chargement de données

## 📄 Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

