# import dependencies 
import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.station
Measurements = Base.classes.measurement
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def homepage():
    return (
        f"<big><big>Available Routes:<small><small><br/>"
        f"- List of previous year rain totals for all stations: <b> /api/v1.0/precipitation </b><br/>" 
        f"- List of station numbers and names: <b> /api/v1.0/stations</b><br/>"
        f"- List of previous year temperatures from all stations: <b> /api/v1.0/tobs </b><br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date: <b> /api/v1.0/start</b><br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive: <b>  /api/v1.0/start/end</b><br/>"
      
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date > last_year).\
        order_by(Measurements.date).all()
    rain_totals = []
    for result in rain:
        row = {}
        row["date"] = rain[0]
        row["prcp"] = rain[1]
        rain_totals.append(row)

    return jsonify(rain_totals)

@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(Measurements.date, Measurements.tobs).\
        filter(Measurements.date > last_year).\
        order_by(Measurements.date).all()
    temperature_totals = []
    for result in temperature:
        row = {}
        row["date"] = temperature[0]
        row["tobs"] = temperature[1]
        temperature_totals.append(row)

    return jsonify(temperature_totals)

@app.route("/api/v1.0/<start>")
def trip1(start):
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    trip_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

if __name__ == "__main__":
    app.run(debug=True)