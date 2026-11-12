import os

from app import app, importer_csv
from models import db

with app.app_context():
    db.drop_all()
    db.create_all()

    exemple = os.path.join(os.path.dirname(__file__), "stations_exemple.csv")
    if os.path.exists(exemple):
        with open(exemple, encoding="utf-8-sig") as f:
            nb, erreurs = importer_csv(f.read())
        print(f"Import de l'exemple : {nb} station(s), {erreurs} erreur(s).")
    else:
        print("Aucun fichier d'exemple trouvé, base vide créée.")

print("Base de données initialisée : stations.db")
