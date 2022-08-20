#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from itertools import groupby
import json
import sys
from timeit import repeat
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  print(current_time)
  # upcoming_shows = Venue.shows.filter(Show.start_time > current_time).all()
  # print(upcoming_shows)
  venues = Venue.query.order_by(Venue.city, Venue.state).all()
  data = []
  for location, venue in groupby(venues, lambda Venue: (Venue.city, Venue.state)):
    city_n_state = {
      "city": location[0],
      "state": location[1],
      "venues": list(venue)
      }
    
    data.append(city_n_state)
    # print(city_n_state["venues"])
    for attr in city_n_state["venues"]:
      print(attr.name)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  if search_term != '':
    print(search_term)
    
    venues = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
    data = []

    for venue in venues:
      print(venue)

      all_upcoming_shows = db.session.query(Show).filter(
        Show.venue_id == venue.id ).filter(
          Show.start_time > datetime.now()).all()

      data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(all_upcoming_shows)
      })

    response={
      "count": len(venues),
      "data": data
    }

  else:
    response={"count": 0}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # replace with real venue data from the venues table, using venue_id

  venues = db.session.query(Venue).get(venue_id)
  # print(venues)
  all_past_shows = db.session.query(Show).join(Artist).filter(
    Show.venue_id == venue_id ).filter(
      Show.start_time < datetime.now()
    ).all()
  print('past_shows', all_past_shows)
  past_shows = []
  
  for show in all_past_shows:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
  })

  all_upcoming_shows = db.session.query(Show).join(Artist).filter(
    Show.venue_id == venue_id ).filter(
      Show.start_time > datetime.now()
    ).all()
  print('upcoming_shows', all_upcoming_shows)
  upcoming_shows = []

  for show in all_upcoming_shows:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  data = {
    "id": venues.id,
    "name": venues.name,
    "genres": venues.genres,
    "address": venues.address,
    "city": venues.city,
    "state": venues.state,
    "phone": venues.phone,
    "website": venues.website,
    "facebook_link": venues.facebook_link,
    "seeking_talent": venues.seeking_talent,
    "seeking_description": venues.seeking_description,
    "image_link": venues.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  # prints each element of the instance created
  for attr, value in data.items():
    print(attr + ' : ', value)

  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error=False
  try:
  # modify data to be the data object returned from db insertion
    venue = Venue(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      address = request.form.get('address'),
      phone = request.form.get('phone'),
      image_link = request.form.get('image_link'),
      genres = request.form.getlist('genres'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website_link'),
      seeking_talent = False if request.form.get('seeking_talent') == None else True,
      seeking_description = request.form.get('seeking_description')
    )
    # prints each element of the instance created
    for attr, value in venue.__dict__.items():
        print(attr + ' : ', value)
    # insert form data as a new Venue record in the db, instead
    db.session.add(venue)
    db.session.commit()   
    # on successful db insert, flash success
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  if not error:
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # replace with real data returned from querying the database
  data = Artist.query.order_by('id').all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  if search_term != '':
    print(search_term)
    
    artists = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
    data = []

    for artist in artists:
      print(artist)

      all_upcoming_shows = db.session.query(Show).filter(
        Show.artist_id == artist.id ).filter(
          Show.start_time > datetime.now()).all()

      data.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": len(all_upcoming_shows)
      })

    response={
      "count": len(artists),
      "data": data
    }
    
  else:
    response={"count": 0}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # replace with real artist data from the artist table, using artist_id
  
  artists = db.session.query(Artist).get(artist_id)
  # print(artists)
  all_past_shows = db.session.query(Show).join(Venue).filter(
    Show.artist_id == artist_id ).filter(
      Show.start_time < datetime.now()
    ).all()
  print('past_shows', all_past_shows)
  past_shows = []
  
  for show in all_past_shows:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
  })

  all_upcoming_shows = db.session.query(Show).join(Venue).filter(
    Show.artist_id == artist_id ).filter(
      Show.start_time > datetime.now()
    ).all()
  print('upcoming_shows', all_upcoming_shows)
  upcoming_shows = []

  for show in all_upcoming_shows:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      # "2035-04-01T20:00:00.000Z"
    })

  data = {
    "id": artists.id,
    "name": artists.name,
    "genres": artists.genres,
    "city": artists.city,
    "state": artists.state,
    "phone": artists.phone,
    "website": artists.website,
    "facebook_link": artists.facebook_link,
    "seeking_venue": artists.seeking_venue,
    "seeking_description": artists.seeking_description,
    "image_link": artists.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  # prints each element of the instance created
  for attr, value in data.items():
    print(attr + ' : ', value)

  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  print(artist)

  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  # prints each element of the instance created
  for attr, value in artist.__dict__.items():
    print(attr + ' : ', value)

  # populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error=False
  artist = Artist.query.get(artist_id)
  print(artist)
  try:
  # modify data to be the data object returned from db insertion
    # artist = Artist(
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.image_link = request.form.get('image_link')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website = request.form.get('website_link')
    artist.seeking_venue = False if request.form.get('seeking_venue') == None else True
    artist.seeking_description = request.form.get('seeking_description')
    # )
    # prints each element of the instance created
    for attr, value in artist.__dict__.items():
        print(attr + ' : ', value)

    db.session.commit()   
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name']  + ' could not be Updated.')
  finally:
    db.session.close()
  if not error:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully Updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name']  + ' could not be Updated.')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  print(venue)
 
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link

  # prints each element of the instance created
  for attr, value in venue.__dict__.items():
    print(attr + ' : ', value)
    
  # populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  print(venue)
  error=False
  try:
  # modify data to be the data object returned from db insertion
    # venue = Venue(
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.image_link = request.form.get('image_link')
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form.get('facebook_link')
    venue.website = request.form.get('website_link')
    venue.seeking_talent = False if request.form.get('seeking_talent') == None else True
    venue.seeking_description = request.form.get('seeking_description')
    # )
    # prints each element of the instance created
    for attr, value in venue.__dict__.items():
        print(attr + ' : ', value)
    # insert form data as a new Venue record in the db, instead

    db.session.commit()   
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  if not error:
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error=False
  try:
  # modify data to be the data object returned from db insertion
    artist = Artist(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      image_link = request.form.get('image_link'),
      genres = request.form.getlist('genres'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website_link'),
      seeking_venue = False if request.form.get('seeking_venue') == None else True,
      seeking_description = request.form.get('seeking_description')
    )
    # prints each element of the instance created
    for attr, value in artist.__dict__.items():
        print(attr + ' : ', value)

  # insert form data as a new Venue record in the db, instead
    db.session.add(artist)
    db.session.commit()   
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name']  + ' could not be listed.')
  finally:
    db.session.close()
  if not error:
    return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # replace with real venues data.

  shows = Show.query.all()

  data = []
  for show in shows:
    data.append({      
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })


  # prints each element of the show 
  for elem in data:
    print(elem)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # insert form data as a new Show record in the db, instead
  error=False
  try:
  # modify data to be the data object returned from db insertion
    show = Show(
      artist_id = request.form.get('artist_id'),
      venue_id = request.form.get('venue_id'),
      start_time = request.form.get('start_time')
    )
    # prints each element of the instance created
    for attr, value in show.__dict__.items():
        print(attr + ' : ', value)

  # insert form data as a new Venue record in the db, instead
    db.session.add(show)
    db.session.commit()   
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  if not error:
    return render_template('pages/home.html')

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
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
