#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
	
from datetime import datetime
from array import array
import json
import babel
import dateutil.parser
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

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:areeg@localhost:5432/fyyurproject'

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String),nullable=False)
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='Venue', lazy=True)
    db.session.commit()
    

    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String),nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_venue = db.Column(db.String())
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='Artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
db.create_all()

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  data=[]
  listofcity = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)

  
  for i in range(listofcity.count()):


    venues = db.session.query(Venue.id, Venue.name).filter(Venue.city == listofcity[i][0]).filter(Venue.state==listofcity[i][1])
    # print(listofcity[i])
    data.append({
      
      "city":listofcity[i][0],
      "state":listofcity[i][1],
      "venues":venues
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  #get data from html and save in variable called searchbasevenuename then query all venue name if
  #  content word like searchbasevenuename save this query in 
  # searchbasevenuename = request.form.get('search_term', '')

  response={
    # take the number of venue that content word like typing in user filed
    "count":db.session.query(Venue).filter(Venue.name.ilike('%' +  request.form.get('search_term', '') + '%')).count() ,
    #return all Venue parameters matched
    "data": db.session.query(Venue).filter(Venue.name.ilike('%' + request.form.get('search_term', '') + '%'))
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # select all Venue properties with id venue_id  i used one() because i retrive only one Venue with id in my database will 
  #retrive to my
  ven = db.session.query(Venue).filter(Venue.id == venue_id).one()

  # may be my Venue have show so i retrive all show match my Venue_id
  shows = db.session.query(Show).filter(Show.venue_id == venue_id).all()
  # create two arry one for retrive venuse show that comming and one for past show 
  upcoming_shows=[]
  past_shows=[]

  for show in shows:
    # each show do with artist so base of artist id i retrive properties of artis from Atrist table such name and imge of it
    # each time i take only one artist so i use one() methods
    artists = db.session.query(Artist.name, Artist.image_link,Artist.id).filter(Artist.id == show.artist_id).one()
    # chek if Venue show in future ot past so if in future added to arry of future if in past added to array of pase and so one 
    if show.start_time < datetime.now():
      #take all required parameter of Artist and save it in past if current time high than time of show
      past_show={
        "artist_id":show.artist_id,
        "artist_name":artists.name,
        "artist_image_link":artists.image_link,
        "start_time":show.start_time
       }
       # append it to array pastshow to save it in data pastshow key
      past_shows.append(past_show)
    else:
       #take all required parameter of Artist and save it in upcoming if current time less than time of show
      coming_show={
        "artist_id":show.artist_id,
        "artist_name":artists.name,
        "artist_image_link":artists.image_link,
        "start_time":show.start_time
       }
      # append it to array pastshow to save it in data pastshow key
      upcoming_shows.append(coming_show)



  data={
    "id":ven.id,
    "name":ven.name,
    "genres":ven.genres,
    "address":ven.address,
    "city":ven.city,
    "state":ven.state,
    "phone":ven.phone,
    "website":ven.website,
    "facebook_link":ven.facebook_link,
    "seeking_talent":ven.seeking_talent,
    "seeking_description":ven.seeking_description,
    "image_link":ven.image_link,
    "past_shows":past_shows,
    "upcoming_shows":upcoming_shows,
    # take length of upcoming show 
    "upcoming_shows_count":len(upcoming_shows),
    # take length of past show 
    "past_shows_count":len(past_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # form = VenueForm(request.form)
  xx=False
  x=request.form.get('seeking_talent')
  if x:
    xx=True

  print(xx)
  new_venue = Venue(
    name = request.form.get('name'),
    genres = request.form.getlist('genres'),
    address = request.form.get('address'),
    city = request.form.get('city'),
    state = request.form.get('state'),
    phone = request.form.get('phone'),
    image_link = request.form.get('image_link'),
    website = request.form.get('website'),
    seeking_talent = xx,
    facebook_link = request.form.get('facebook_link'),
    seeking_description = request.form.get('seeking_description'))
  
  try:
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue   was successfully listed!')
  except:
      flash('An error occurred. Venue  could not be added.')
  finally:
      db.session.close()
  return render_template('pages/home.html')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['post'])
def delete_venue(venue_id):
  
  try:
    db.session.query(Venue).filter(Venue.id == venue_id).delete()
    db.session.commit()
    flash('deleted successfuly')
  except:
    flash('error appear')
  finally:
    db.session.close()
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  listofartists = db.session.query(Artist.id, Artist.name)
  data=listofartists
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response=[]
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  #query all artist by user name and id
  qartist=db.session.query(Artist.id,Artist.name).filter(Artist.name.ilike('%' +  request.form.get('search_term') + '%')).all()
  data=[]
  #loop for artist to select it id and name to send to page
  for i in qartist:
    upcomingshow=2
    #loop on show to check if the artist have a new show or not by check it starttime with current time in reall word
    qshow = db.session.query(Show.start_time).filter(Show.artist_id == i.id).all()
    for ii in qshow:
      print(ii.start_time)
      if ii.start_time > datetime.now():
        # increased upcomingshow if we have new shows
        upcomingshow+=1
    #append id, name , number of comingshow in data to apped it again to respons becuse count can not be used in loop
    data.append({
      "id":i.id,
      "name":i.name,
      "num_upcoming_shows":upcomingshow
      })
    
   #apped above data to response 
  response={
    "count":len(qartist),
    "data": data,
    }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id

  comming_venue=[]
  past_venue=[]

  artists = db.session.query(Artist).filter(Artist.id == artist_id).one()
  shows = db.session.query(Show).filter(Show.artist_id == artist_id).all()
  for show in shows:
    venue = db.session.query(Venue.id,Venue.name,Venue.image_link).filter(Venue.id == show.venue_id).one()
    if show.start_time > datetime.now():
      data_of_show={
        "venue_id":show.id,
        "venue_name":venue.name,
        "venue_image_link":venue.image_link,
        "start_time":str(show.start_time)
      }
      comming_venue.append(data_of_show)
    else:
      data_of_sho={
          "venue_id":show.id,
          "venue_name":venue.name,
          "venue_image_link":venue.image_link,
          "start_time":str(show.start_time)
        }
      past_venue.append(data_of_sho)
  data={
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
    "past_shows": past_venue,
    "upcoming_shows": comming_venue,
    "past_shows_count": len(past_venue),
    "upcoming_shows_count": len(comming_venue),
    }
    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  form = ArtistForm()
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  # artist = db.session.query(Artist).filter(Artist.id == artist_id).one()

  seek = False
  if request.form.get('seeking_venue'):
    seek = True

  artist_modifiy = {
    'name':request.form.get('name'),
    'city' :request.form.get('city'),
    'state' :request.form.get('state'),
    'phone' :request.form.get('phone'),
    'facebook_link':request.form.get('facebook_link'),
    'genres' :request.form.getlist('genres'),
    'website': request.form.get('website'),
    'image_link':request.form.get('image_link'),
    'seeking_venue' :seek,
    'seeking_description' :request.form.get('seeking_description')
  }

  try:
    db.session.query(Artist).filter(Artist.id == artist_id).update(artist_modifiy)
    db.session.commit()
    flash('okkkkkkkkkkkkkkk  ' +request.form.get('name'))
  except:
    flash('soory not update ')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm()
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):


  seek = False
  if request.form.get('seeking_talent'):
    seek = True

  edit_venue = {
    'name':request.form.get('name'),
    'city' :request.form.get('city'),
    'state' :request.form.get('state'),
    'phone' :request.form.get('phone'),
    'facebook_link':request.form.get('facebook_link'),
    'genres' :request.form.getlist('genres'),
    'website': request.form.get('website'),
    'image_link':request.form.get('image_link'),
    'seeking_talent':seek,
    'seeking_description' :request.form.get('seeking_description')
  }

  try:
    db.session.query(Venue).filter(Venue.id == venue_id).update(edit_venue)
    db.session.commit()
    flash('Nice updat oky')
  except:
    flash('Sorry  some thing went error')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  sekking=False
  if request.form.get('seeking_venue'):
    sekking =True

  new_artist = Artist(
    name = request.form.get('name'),
    city = request.form.get('city'),
    state = request.form.get('state'),
    phone = request.form.get('phone'),
    genres = request.form.getlist('genres'),
    image_link = request.form.get('image_link'),
    facebook_link = request.form.get('facebook_link'),
    seeking_description = request.form.get('seeking_description'),
    seeking_venue = sekking,
    website = request.form.get('website')
  )

  try:
    db.session.add(new_artist)
    db.session.commit()
  except:
    flash('An error occurred. Show could not be added.')
  finally:
    db.session.close()

  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  data=[]
  show = db.session.query(Show.venue_id,Show.artist_id,Show.start_time).all()
  for i in show:
    venue = db.session.query(Venue.id, Venue.name).filter(Venue.id == i.venue_id)
    artist = db.session.query(Artist.id, Artist.name, Artist.image_link).filter(Artist.id == i.artist_id)
    j=0
    # print(artist[j][2])
    
    data.append({
      "venue_id": i.venue_id,
      "venue_name":venue[j][1],
      "artist_id":i.artist_id,
      "artist_name":artist[j][1],
      "artist_image_link":artist[j][2],
      "start_time":str(i.start_time)
    })
    j+=1
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  new_show = Show(
    venue_id = request.form.get('venue_id'),
    artist_id = request.form.get('artist_id'),
    start_time = request.form.get('start_time')
  )

  try:
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
      flash('An error occurred. Show could not be added.')
  finally:
      db.session.close()

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
