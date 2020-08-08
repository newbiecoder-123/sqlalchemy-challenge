### Building an API

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Create our session (link) from Python to the DB
session = Session(engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of stations /api/v1.0/stations<br/>"
        f"List of temperature: /api/v1.0/tobs<br/>"
        f"Data from start date 'yyyy-mm-dd': /api/v1.0/yyyy-mm-dd<start><br/>"
        f"Data between start and end date in 'yyyy-mm-dd': /api/v1.0/yyyy-mm-dd<start>/yyyy-mm-dd<end>"    
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a list of all dates and precipitation results"""
    # Query all dates and precipitation results
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).all()
    
    session.close()

    date_prcp = []
    for date, precipitation in results:
        date_prcp_dict = {}
        date_prcp_dict["date"] = date
        date_prcp_dict["prcp"] = precipitation
        date_prcp.append(date_prcp_dict)
        
    return jsonify(date_prcp)

@app.route("/api/v1.0/stations")
def station():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the station names
    results = session.query(Station.name).all()
    
    session.close()
    
    # Convert list of tuples into normal list
    station_names = list(np.ravel(results))

    return jsonify(station_names)

    
@app.route("/api/v1.0/tobs")
def temp():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the most active station
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    sel = [Measurement.date,
           Measurement.tobs]
   
    last_12_months = session.query(*sel).filter(Measurement.date >= query_date).order_by(Measurement.date.desc()).all()
    
    session.close()
    
    date_temp = []
    for date, temp in last_12_months:
        date_temp_dict = {}
        date_temp_dict["date"] = date
        date_temp_dict["temp"] = temp
        date_temp.append(date_temp_dict)
    
    return jsonify(date_temp)

@app.route("/api/v1.0/<start>")
def start_date(start):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [func.min(Measurement.tobs), 
       func.avg(Measurement.tobs),
       func.max(Measurement.tobs)]

    results = session.query(*sel).filter(Measurement.date >= start).all()
    
    session.close()
    
    date_temp_summary = []
    
    for min_temp, avg_temp, max_temp in results:
        summary_date_temp_dict = {}
        summary_date_temp_dict["Min Temp"] = min_temp
        summary_date_temp_dict["Avg Temp"] = avg_temp
        summary_date_temp_dict["Max Temp"] = max_temp
        date_temp_summary.append(summary_date_temp_dict)
        
    return jsonify(date_temp_summary)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_and_end_date(start_date, end_date):    
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [func.min(Measurement.tobs), 
       func.avg(Measurement.tobs),
       func.max(Measurement.tobs)]

    results = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    session.close()
    
    date_temp_summary = []
    
    for min_temp, avg_temp, max_temp in results:
        summary_date_temp_dict = {}
        summary_date_temp_dict["Min Temp"] = min_temp
        summary_date_temp_dict["Avg Temp"] = avg_temp
        summary_date_temp_dict["Max Temp"] = max_temp
        date_temp_summary.append(summary_date_temp_dict)
        
    return jsonify(date_temp_summary)
    
if __name__ == '__main__':
    app.run(debug=True)
