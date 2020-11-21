from app import db
# from sqlalchemy import ARRAY
from datetime import datetime

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String()))
    facebook_link = db.Column(db.String(500))

    website  = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description =  db.Column(db.String(120))
    shows = db.relationship('Show', backref='venues', lazy='dynamic', passive_deletes=True)

    def __repr__(self):
          return f'<Venue {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))

    website  = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description =  db.Column(db.String(120))
    shows = db.relationship('Show', backref='artists', lazy=True, passive_deletes=True)

    def __repr__(self):
          return f'<Artist {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete='CASCADE'), nullable=False)
    # upcoming_show = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Show {self.id} {self.start_time} >'


db.create_all()