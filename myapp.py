#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
from flask_migrate import Migrate, MigrateCommand
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate=Migrate(app,db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
db.create_all()

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
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues=Venue.query.all()
  venuesDictList=get_child_data(venues)
  venuesDictListCleaned=[clean_sql_to_dict(venueDictList) for venueDictList in venuesDictList ]

  for venueDictList in venuesDictListCleaned:
      for show in venueDictList['upcoming_shows']:
          showQuery=Artist.query.get(show['artist_id'])
          show['artist_name']=showQuery.name
          show['artist_image_link']=showQuery.image_link
          show['start_time']=show['start_time'].strftime("%m/%d/%Y, %H:%M:%S")

  cities={}
  for venue in venuesDictListCleaned:
      newVenue={}
      newVenue['id']=venue['id']
      newVenue['name']=venue['name']
      newVenue['num_upcoming_shows']=venue['upcoming_shows_count']

      if venue['city'] not in cities:
          cities[venue['city']]={}
          cities[venue['city']]['city']=venue['city']
          cities[venue['city']]['state']=venue['state']
          cities[venue['city']]['venues']=[]


      cities[venue['city']]['venues'].append(newVenue)


  data=[v for v in cities.values()]

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', None)
  venues = Venue.query.filter(
    Venue.name.ilike("%{}%".format(search_term))).all()

  tests=get_child_data(venues)
  tests2=[clean_sql_to_dict(test) for test in tests]


  response2 = {
        "count": len(venues),
        "data": [{'id':test2['id'],'name':test2['name'],'num_upcoming_shows':test2['upcoming_shows_count'] } for test2 in tests2]
    }
  return render_template('pages/search_venues.html', results=response2, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue=Venue.query.get(venue_id)
  venueChild=get_child_data([venue])
  data=clean_sql_to_dict(venueChild[0])
  data['genres']=data['genres'].split(',')

  for show in data['past_shows']:
      showQuery=Artist.query.get(show['artist_id'])
      show['artist_name']=showQuery.name
      show['artist_image_link']=showQuery.image_link
      show['start_time']=show['start_time'].strftime("%m/%d/%Y, %H:%M:%S")

  for show in data['upcoming_shows']:
      showQuery=Artist.query.get(show['artist_id'])
      show['artist_name']=showQuery.name
      show['artist_image_link']=showQuery.image_link
      show['start_time']=show['start_time'].strftime("%m/%d/%Y, %H:%M:%S")

  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

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
    venue_form = VenueForm(request.form)

    try:
        new_venue = Venue(
            name=venue_form.name.data,
            genres=','.join(venue_form.genres.data),
            address=venue_form.address.data,
            city=venue_form.city.data,
            state=venue_form.state.data,
            phone=venue_form.phone.data,
            facebook_link=venue_form.facebook_link.data,
            )

        db.session.add(new_venue)
        db.session.rollback()
        # on successful db insert, flash success
        flash('Venue ' +
              venue_form.name.data +
              ' was successfully listed!')
    except Exception as ex:
        flash('An error has occurred. Venue ' +
              venue_form.name.data + ' could not be listed.')
        traceback.print_exc()
  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venueToDelete = Venue.query.get(venue_id)
  db.session.delete(venueToDelete)
  db.session.commit()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists=Artist.query.all()
  data=[{'id':artist.id,'name':artist.name} for artist in artists]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

 search_term = request.form.get('search_term', None)
 artists = Artist.query.filter(
    Artist.name.ilike("%{}%".format(search_term))).all()

 tests=get_child_data(artists)
 tests2=[clean_sql_to_dict(test) for test in tests]
 response2={
 "count":len(artists),
 "data": [{'id':test2['id'],'name':test2['name'],'num_upcoming_shows':test2['upcoming_shows_count'] } for test2 in tests2]
 }

 return render_template('pages/search_artists.html', results=response2, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist=Artist.query.get(artist_id)
  artistChild=get_child_data([artist])
  data=clean_sql_to_dict(artistChild[0])
  data['genres']=data['genres'].split(',')

  for show in data['past_shows']:
      showQuery=Venue.query.get(show['venue_id'])
      show['venue_name']=showQuery.name
      show['venue_image_link']=showQuery.image_link
      show['start_time']=show['start_time'].strftime("%m/%d/%Y, %H:%M:%S")

  for show in data['upcoming_shows']:
      showQuery=Venue.query.get(show['venue_id'])
      show['venue_name']=showQuery.name
      show['venue_image_link']=showQuery.image_link
      show['start_time']=show['start_time'].strftime("%m/%d/%Y, %H:%M:%S")

  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_query=Artist.query.get(artist_id)
  #tranform the query to a dict, clean undesirables and use it
  #as input for the ArtistForm function
  form = ArtistForm(clean_sql_to_dict(artist_query.__dict__))

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    artist_form = ArtistForm(request.form)
    try:
        artist = Artist.query.filter_by(id=artist_id).one()
        artist.name = artist_form.name.data,
        artist.genres = json.dumps(form.genres.data),  # array json
        artist.city = artist_form.city.data,
        artist.state = artist_form.state.data,
        artist.phone = artist_form.phone.data,
        artist.facebook_link = artist_form.facebook_link.data,
        artist.image_link = artist_form.image_link.data,
        db.session.update(artist)
        # on successful db insert, flash success
        flash('Artist ' + form.name.data + ' was successfully updated!')
    except Exception as e:
        flash('An error occurred. Artist ' +
              request.form.name + ' could not be updated.')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  venue_query=Venue.query.get(artist_id)
    #tranform the query to a dict, clean undesirables and use it
    #as input for the ArtistForm function
  form = VenueForm(clean_sql_to_dict(venue_query.__dict__))
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
      venue_form = VenueForm(request.form)
      try:
          venue = Venue.query.filter_by(id=venue_id).one()
          venue.name = venue_form.name.data,
          venue.genres = json.dumps(form.genres.data),  # array json
          venue.city = venue_form.city.data,
          venue.state = venue_form.state.data,
          venue.phone = venue_form.phone.data,
          venue.facebook_link = venue_form.facebook_link.data,
          venue.image_link = venue_form.image_link.data,
          db.session.update(venue)
          # on successful db insert, flash success
          flash('Venue ' + form.name.data + ' was successfully updated!')
      except Exception as e:
          flash('An error occurred. Venue ' +
                request.form.name + ' could not be updated.')
      return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    artist_form = ArtistForm(request.form)
    try:
        new_artist = Artist(
            name=artist_form.name.data,
            genres=','.join(artist_form.genres.data),
            city=artist_form.city.data,
            state=artist_form.state.data,
            phone=artist_form.phone.data,
            facebook_link=artist_form.facebook_link.data)


        db.session.add(new_artist)
        db.session.rollback()

        # on successful db insert, flash success
        flash('Artist ' + artist_form.name.data + ' was successfully listed!')
    except Exception as ex:
        flash('An error occurred. Artist ' +
              artist_form.name.data + ' could not be listed.')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows=Show.query.all()
  shows=[show.__dict__ for show in shows]
  for show in shows:
      venueQuery=Venue.query.get(show['venue_id'])
      artistQuery=Artist.query.get(show['artist_id'])

      show['venue_name']=venueQuery.name
      show['venue_image_link']=venueQuery.image_link
      show['artist_name']=artistQuery.name
      show['artist_image_link']=artistQuery.image_link
      show['start_time']=show['start_time'].strftime("%m/%d/%Y, %H:%M:%S")

  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    show_form = ShowForm(request.form)
    try:
        show = Show(
            artist_id=show_form.artist_id.data,
            venue_id=show_form.venue_id.data,
            start_time=show_form.start_time.data
        )
        #show.add()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception as e:
        flash('An error occurred. Show could not be listed.')

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
