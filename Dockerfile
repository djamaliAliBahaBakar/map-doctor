#Image based on official Python 3.12.3 image
FROM python:3.12.3

#Dossier de travail dans le conteneur
WORKDIR /app

#Copie du fichier requirements.txt dans le conteneur
COPY requirements.txt .

#Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y libgomp1 && apt-get clean
RUN pip install --no-cache-dir -r requirements.txt

# Copie du contenu du répertoire courant dans le conteneur
COPY . .

#Commande pour lancer l'application
EXPOSE 8501

CMD ["streamlit", "run", "app.py"]


