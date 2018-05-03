#Dependencies
import pandas as pd
import numpy as np
import datetime as dt
from flask import Flask, jsonify

#Import python for SQL and ORM
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#Create database connection
engine = create_engine("sqlite:///hawaii.sqlite")

#Reflect existing database as new model
Base = automap_base()
#Reflect tables
Base.prepare(engine, reflect= True)

#Declare variable to reference each table
Measurement = Base.classes.measurement 
Station = Base.classes.station

#Link Python to database
session = Session(engine)

#Create Flask setup
app = Flask(__name__)

#Create Flask routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the HCOD (Hawaii Climate Open Database)!<br/>"
        f"Avalable Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )
#Return Hawaii precipitation data for the last year
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Calculate the date one year previous from today's date
    one_year_ago = dt.date.today() - dt.timedelta(days=365)

    #Query to retrieve wanted data from table in database
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    #Create dictionary using query
    precipitation = {date: prcp for date, prcp in data}
    return jsonify(precipitation)

#Return list of stations from dataset
@app.route("/api/v1.0/stations")
def stations():
    #Query to retrieve all stations
    results = session.query(Station.station).all()

    #Create list of stations
    stations = list(np.ravel(results))
    return jsonify(stations)

#Return temperature observations (tobs) for previous year
@app.route("/api/v1.0/tobs")
def tobs():

    #Calculate the date one year previous from today's date
    one_year_ago = dt.date.today() - dt.timedelta(days=365)

    #Query for tobs from previous year
    results = session.query(Measurement.tobs).\
        filter(Measurement.date >= one_year_ago).all()
    
    #Create list of tobs
    temps = list(np.ravel(results))
    return jsonify(temps)

@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run()
