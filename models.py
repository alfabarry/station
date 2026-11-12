from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Station(db.Model):
    __tablename__ = "stations"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    commune = db.Column(db.String(100), index=True)
    prefecture = db.Column(db.String(100), index=True)

    def __repr__(self):
        return f"<Station {self.nom}>"
