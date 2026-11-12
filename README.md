# ⛽ Stations de carburant — Application Flask

Application simple de gestion de stations de carburant : nom, coordonnées géographiques (latitude/longitude), commune et préfecture.

## Fonctionnalités

- Liste des stations avec **recherche par nom** et **filtres par commune / préfecture**
- **Ajout, modification et suppression** des stations (formulaires validés)
- **Import CSV** en masse (séparateur `;` ou `,`, encodage UTF-8)
- **Export CSV** de toutes les données
- **Carte interactive** (OpenStreetMap / Leaflet) avec un marqueur par station
- Lien « voir sur OpenStreetMap » pour chaque station

## Installation

```bash
pip install -r requirements.txt
python init_db.py        # crée la base stations.db + importe l'exemple
python app.py            # démarre le serveur
```

Puis ouvrir http://127.0.0.1:5000

## Format du CSV d'import

```csv
nom;latitude;longitude;commune;prefecture
Total Agdal;34.00820;-6.84980;Rabat;Rabat-Salé-Kénitra
```

Les colonnes doivent être nommées `nom`, `latitude`, `longitude`, `commune`, `prefecture` (la virgule est aussi acceptée comme séparateur, et les décimales avec virgule `34,008` sont converties).

## Structure

```
stations_app/
├── app.py                  # Application Flask (routes + import/export CSV)
├── models.py               # Modèle Station (SQLAlchemy)
├── forms.py                # Formulaires (Flask-WTF)
├── init_db.py              # Création de la base + données d'exemple
├── requirements.txt
├── stations_exemple.csv    # Jeu de données de démonstration
└── templates/              # Interface Bootstrap 5 en français
```

## Production

Définir une `SECRET_KEY` et utiliser un serveur WSGI :

```bash
export SECRET_KEY="une-longue-valeur-aléatoire"
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:8000 "app:app"
```
