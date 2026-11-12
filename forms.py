from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class StationForm(FlaskForm):
    nom = StringField("Nom de la station", validators=[DataRequired(), Length(max=150)])
    latitude = DecimalField(
        "Latitude",
        places=6,
        validators=[DataRequired(), NumberRange(min=-90, max=90)],
    )
    longitude = DecimalField(
        "Longitude",
        places=6,
        validators=[DataRequired(), NumberRange(min=-180, max=180)],
    )
    commune = StringField("Commune", validators=[Optional(), Length(max=100)])
    prefecture = StringField("Préfecture", validators=[Optional(), Length(max=100)])
    submit = SubmitField("Enregistrer")


class ImportForm(FlaskForm):
    submit = SubmitField("Importer le fichier")
