
# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
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
from flask_migrate import Migrate

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime
def clean_sql_to_dict(myInput):
    """
    removes all keys that have values that are not either sqlAlchemy objects or
    other undesirables

    INPUT:
    myInput: mySQL query object in a dict form ex: myQuery.__dict__
    """
    output={}
    for k,v in myInput.items():

        if k=='_sa_instance_state' or k=='shows':
            pass
        elif type(v)==type(list()):
            print(k)
            output[k]=[clean_sql_to_dict(item) for item in v]

        elif type(v)==type(dict()):
            output[k]=clean_sql_to_dict(v,output)
        else:
            output[k]=v

    return output


#myvenue=session.query(app.Venue).get(3)

def get_child_data(allParents):
    """
    tranforms a SqlAlchemy object into a dictionary

    INPUTS:
    allParents=list of SqlAlchemy object from a given Query
    OUPUTS:
    output: list of dictionaries with parent data and child data
    """
    outputData=[]
    for parent in allParents:
        parent.shows #get the shows of the parent

        parentDict=parent.__dict__
        #additional data for segmenting shows children
        parentDict['past_shows']=[]
        parentDict['upcoming_shows']=[]


        dictShows=[show.__dict__ for show in parent.shows]

        for show in dictShows:
            if show['start_time']<datetime.now():
                parentDict['past_shows'].append(show)

            else:
                parentDict['upcoming_shows'].append(show)

        parentDict['past_shows_count']=len(parentDict['past_shows'])
        parentDict['upcoming_shows_count']=len(parentDict['upcoming_shows'])

        output={}
        cleanParentDict=clean_sql_to_dict(parentDict) #remove unwanted fields
        outputData.append(cleanParentDict)
    return outputData

def select_fields(listDataObj,keys):
    listDataObjFiltered=[]

    for dataObj  in listDataObj:
        dataObj=dataObj.__dict__
        listDataObjFiltered.append({key:dataObj[key] for key in keys})
    return listDataObjFiltered

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    genres=db.Column(db.String(300))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(250))
    seeking_talent = db.Column(db.Boolean,default=False)
    shows = db.relationship('Show',backref='venue',collection_class=list)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    def __repr__(self):
        return f'<Venue {self.id}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean,default=False)
    shows = db.relationship('Show',backref='artist',collection_class=list)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    def __repr__(self):
        return f'<Artist {self.id}>'

class Show(db.Model):
    __tablename__='Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id'), nullable=False)
    def __repr__(self):
        return f'<Show {self.id}>'
# TODO Implement Show and Artist models, a
