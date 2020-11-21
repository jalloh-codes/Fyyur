#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import os
from datetime import datetime
from flask_migrate import Migrate
from models import *
from flask_wtf import Form
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database


# artist_id={artist_id} venue_id={venue_id}

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#------------------------------------ ----------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data. uld be aggregated based on number of upcoming shows per venue.
  time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
  city_state_array = []

  data = list()
  try:
    for venue in venues:
      num_upcoming_shows = venue.shows.filter(Show.start_time > time).all()
      if   venue.city + venue.state in city_state_array:
        data[-1]["venues"].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(num_upcoming_shows),
        })
      else:
        city_state_array.append(venue.city + venue.state)
        data.append({
          "city": venue.city,
          "state": venue.state,
          "venues":[{
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(num_upcoming_shows)
          }]
        })
    return render_template('pages/venues.html', areas=data);
  except Exception as e:
    abort(500)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  try:
    time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
    search=  request.form.get('search_term', '').strip()
    venues =  Venue.query.filter(Venue.name.ilike(f'%{search}%')).all()
    # print(venues)
    response = list()
    data = list()
    for venue in venues:
      num_upcoming_shows = venue.shows.filter(Show.start_time > time).all()
      data.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(num_upcoming_shows)
      })
    response.append({
      'count': len(venues),
      'data': data
    })
    return render_template('pages/search_venues.html', results=response[0], search_term=search)
  except:
    abort(404)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  time = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
  venue = Venue.query.get(venue_id)

  past_shows = list()
  upcoming_shows = list()

  coming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time > time).all()
  old_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time <  time).all()
 
  try:
    for show in coming_shows:
      print(show.start_time)
      upcoming_shows.append({
        'artist_id': show.artists.id,
        'artist_name': show.artists.name,
        'artist_image_link': show.artists.image_link,
        'start_time': format_datetime(str(show.start_time))  
      })
    for show in old_shows:
      past_shows.append({
        'artist_id': show.artists.id,
        'artist_name': show.artists.name,
        'artist_image_link': show.artists.image_link,
        'start_time': format_datetime(str(show.start_time)) 
      })
    data={
      'id': venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      'past_shows': past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(coming_shows),
    }
    return render_template('pages/show_venue.html', venue=data)
  except:
    abort(404)

  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    if(request.form.get('seeking_talent') == 'False'):
      seeking_talent = False
    else:
      seeking_talent = True
    form = VenueForm()

    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres= request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_talent=  seeking_talent
    seeking_description = request.form['seeking_description']
    
    venue = Venue(name=name, city=city, state=state,
    address=address, phone=phone, image_link=image_link,  genres=genres,
    facebook_link=facebook_link,  website=website,
    seeking_talent= seeking_talent,  seeking_description=seeking_description)
    
    db.session.add(venue)
    db.session.commit()

    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('index'))
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    abort(500)
  finally:
    db.session.close()

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<int:venue_id>', methods=['POST'])
def delete_venue(venue_id): 
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    # venue = Venue.query.get(venue_id)
    db.session.query(Venue).filter(Venue.id == venue_id).delete()
    # db.session.delete(venue)
    flash('Venue succesfully deleted')
    db.session.commit()
    return redirect(url_for('index'))
  except Exception as e:
    print(e)
    db.session.rollback()
    flash("Venue can't be deleted")
    abort(500)
  finally:
    db.session.close()


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = list()
  artists = Artist.query.with_entities(Artist.id, Artist.name).group_by(Artist.id).all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  search=  request.form.get('search_term', '')
  artists =  Artist.query.filter(Artist.name.ilike(f'%{search}%')).all()

  response = list()
  data = list()

  for artist in artists:
    num_upcoming_shows = len(artist.shows.filter(Show.start_time > time).all())
    print(num_upcoming_shows)
    data.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': num_upcoming_shows
    })
  response.append({
    'count': len(artists),
    'data': data
  })

  print(response)

  return render_template('pages/search_artists.html', results=response[0], search_term=search)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  artist = Artist.query.get(artist_id)
  time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  coming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time > time).all()
  old_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time < time).all()
  print(coming_shows)
  past_shows = list()
  upcoming_shows = list()
  print(len(coming_shows))

  if artist:
    for show in coming_shows:
      upcoming_shows.append({
        'venue_id': show.venues.id,
        'venue_name': show.venues.name,
        'venue_image_link': show.venues.image_link,
        'start_time': format_datetime(str(show.start_time)) 
      })
    for show in old_shows:
      print(show.venues.image_link)
      past_shows.append({
        'venue_id': show.venues.id,
        'venue_name': show.venues.name,
        'venue_image_link': show.venues.image_link,
        'start_time': format_datetime(str(show.start_time)) 
      })
    data={
      'id': artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      'past_shows': past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(coming_shows),
    }
    return render_template('pages/show_artist.html', artist=data)
  else:
    abort(404)

      
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist = Artist.query.get(artist_id)
  if(artist):
    form= ArtistForm(
      id= 4,
      name= artist.name,
      genres= artist.genres,
      city= artist.city,
      state= artist.state,
      phone= artist.phone,
      website= artist.website,
      facebook_link= artist.facebook_link,
      seeking_venue= artist.seeking_venue,
      seeking_description= artist.seeking_description,
      image_link= artist.image_link
    )
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  else:
    abort(404)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.filter_by(id=artist_id).first()
  name = artist.name
  try:
    if(request.form.get('seeking_venue') == 'False'):
      seeking_venue = False
    else:
      seeking_venue = True
    artist.name = request.form['name'],
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres= request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    artist.seeking_venue= seeking_venue
    artist.seeking_description = request.form['seeking_description']

    db.session.commit()
    flash('Artist, '+ name +' updated to ' + request.form['name'] )
    return redirect(url_for('show_artist', artist_id=artist_id))
  except:
    db.session.rollback()
    flash("Artist can't be saved")
    abort(500)
  finally:
    db.session.close()


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue:
    form = VenueForm(
      id = venue.id,
      name = venue.name,
      genres = venue.genres,
      address = venue.address,
      city= venue.city,
      state = venue.state,
      phone = venue.phone,
      website = venue.website,
      facebook_link = venue.facebook_link,
      seeking_talent = venue.seeking_talent,
      seeking_description = venue.seeking_description,
      image_link= venue.image_link
    )
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  else:
    abort(404)
  # TODO: populate form with values from venue with ID <venue_id>
  

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.filter_by(id=venue_id).first()
  name = venue.name
  try:
    error = False
    if(request.form.get('seeking_talent') == 'False'):
          seeking_talent = False
    else:
      seeking_talent = True

    venue.name = request.form['name'],
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.genres= request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.seeking_talent= seeking_talent
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()

  except:
    error = True
    db.session.rollback()

  finally:
    db.session.close()
    if not error:
      flash('Venue, '+ name +' updated to ' + request.form['name'] )
      return redirect(url_for('show_venue', venue_id=venue_id))
    else:
      flash("Artist can't be saved")
      abort(500)
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)
  
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    if(request.form.get('seeking_venue') == 'False'):
      seeking_venue = False
    else:
      seeking_venue = True
    form = ArtistForm()

    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres= request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_venue= seeking_venue
    seeking_description = request.form['seeking_description']

    artist = Artist(name=name, city=city, state=state,
    phone=phone,  genres=genres, image_link=image_link,
    facebook_link=facebook_link,
    website=website, seeking_venue=seeking_venue,
    seeking_description=seeking_description)

    db.session.add(artist)
    db.session.commit()

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('index'))
  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
    abort(500)
  finally:
    db.session.close()
    
    

  # on successful db insert, flash success
 
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
 


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = db.session.query(Show).join(Venue).join(Artist).all()

  data = list()
  for show in shows:

    data.append({
      'venue_id': show.venues.id,
      'venue_name': show.venues.name,
      'artist_id': show.artists.id,
      'artist_name': show.artists.name,
      'artist_image_link': show.artists.image_link,
      'start_time':  format_datetime(str(show.start_time)) 
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    form = ShowForm()
    artist_id = int(request.form['artist_id']),
    venue_id = int(request.form['venue_id']),
    start_time = request.form['start_time'],
    upcoming_show = True
    show = Show(start_time=start_time, artist_id=artist_id, venue_id=venue_id)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
    return redirect(url_for('index'))
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    abort(500)    
  finally:
    db.session.close()

  # on successful db insert, flash success
 
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port)

