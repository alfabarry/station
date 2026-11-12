import csv
import io
import os

from flask import (
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_wtf import CSRFProtect

from forms import ImportForm, StationForm
from models import Station, db

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        BASE_DIR, "stations.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    CSRFProtect(app)
    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


def register_routes(app):
    @app.route("/")
    def index():
        query = Station.query

        recherche = request.args.get("q", "").strip()
        commune = request.args.get("commune", "").strip()
        prefecture = request.args.get("prefecture", "").strip()

        if recherche:
            query = query.filter(Station.nom.ilike(f"%{recherche}%"))
        if commune:
            query = query.filter(Station.commune == commune)
        if prefecture:
            query = query.filter(Station.prefecture == prefecture)

        stations = query.order_by(Station.nom).all()
        communes = [c[0] for c in db.session.query(Station.commune).distinct().order_by(Station.commune) if c[0]]
        prefectures = [p[0] for p in db.session.query(Station.prefecture).distinct().order_by(Station.prefecture) if p[0]]

        return render_template(
            "index.html",
            stations=stations,
            communes=communes,
            prefectures=prefectures,
            recherche=recherche,
            commune=commune,
            prefecture=prefecture,
        )

    @app.route("/station/nouvelle", methods=["GET", "POST"])
    def nouvelle_station():
        form = StationForm()
        if form.validate_on_submit():
            station = Station(
                nom=form.nom.data.strip(),
                latitude=float(form.latitude.data),
                longitude=float(form.longitude.data),
                commune=(form.commune.data or "").strip(),
                prefecture=(form.prefecture.data or "").strip(),
            )
            db.session.add(station)
            db.session.commit()
            flash(f"Station « {station.nom} » ajoutée avec succès.", "success")
            return redirect(url_for("index"))
        return render_template("form.html", form=form, titre="Ajouter une station")

    @app.route("/station/<int:station_id>/modifier", methods=["GET", "POST"])
    def modifier_station(station_id):
        station = db.get_or_404(Station, station_id)
        form = StationForm(obj=station)
        if form.validate_on_submit():
            station.nom = form.nom.data.strip()
            station.latitude = float(form.latitude.data)
            station.longitude = float(form.longitude.data)
            station.commune = (form.commune.data or "").strip()
            station.prefecture = (form.prefecture.data or "").strip()
            db.session.commit()
            flash(f"Station « {station.nom} » mise à jour.", "success")
            return redirect(url_for("index"))
        return render_template("form.html", form=form, titre="Modifier la station")

    @app.route("/station/<int:station_id>/supprimer", methods=["POST"])
    def supprimer_station(station_id):
        station = db.get_or_404(Station, station_id)
        db.session.delete(station)
        db.session.commit()
        flash(f"Station « {station.nom} » supprimée.", "success")
        return redirect(url_for("index"))

    @app.route("/import", methods=["GET", "POST"])
    def importer():
        form = ImportForm()
        if form.validate_on_submit():
            fichier = request.files.get("fichier")
            if not fichier or not fichier.filename.lower().endswith((".csv", ".txt")):
                flash("Veuillez choisir un fichier CSV.", "danger")
                return redirect(url_for("importer"))
            try:
                contenu = fichier.stream.read().decode("utf-8-sig")
                nb, erreurs = importer_csv(contenu)
            except UnicodeDecodeError:
                flash("Le fichier doit être encodé en UTF-8.", "danger")
                return redirect(url_for("importer"))
            if nb:
                flash(f"{nb} station(s) importée(s).", "success")
            if erreurs:
                flash(f"{erreurs} ligne(s) ignorée(s) (format invalide).", "warning")
            return redirect(url_for("index"))
        return render_template("import.html", form=form)

    @app.route("/export")
    def exporter():
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";")
        writer.writerow(["nom", "latitude", "longitude", "commune", "prefecture"])
        for station in Station.query.order_by(Station.nom).all():
            writer.writerow(
                [station.nom, station.latitude, station.longitude, station.commune, station.prefecture]
            )
        return Response(
            buffer.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=stations.csv"},
        )

    @app.route("/carte")
    def carte():
        stations = Station.query.all()
        donnees = [
            {
                "nom": s.nom,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "commune": s.commune,
                "prefecture": s.prefecture,
            }
            for s in stations
        ]
        return render_template("map.html", stations=donnees)


def importer_csv(contenu):
    lecteur = csv.DictReader(io.StringIO(contenu), delimiter=";")
    if not lecteur.fieldnames or "nom" not in [c.strip().lower() for c in lecteur.fieldnames]:
        lecteur = csv.DictReader(io.StringIO(contenu))
    nb, erreurs = 0, 0
    for ligne in lecteur:
        ligne = {(k or "").strip().lower(): (v or "").strip() for k, v in ligne.items()}
        try:
            station = Station(
                nom=ligne["nom"],
                latitude=float(ligne["latitude"].replace(",", ".")),
                longitude=float(ligne["longitude"].replace(",", ".")),
                commune=ligne.get("commune", ""),
                prefecture=ligne.get("prefecture", ""),
            )
            if not -90 <= station.latitude <= 90 or not -180 <= station.longitude <= 180:
                raise ValueError
            db.session.add(station)
            nb += 1
        except (KeyError, TypeError, ValueError):
            erreurs += 1
    db.session.commit()
    return nb, erreurs


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
