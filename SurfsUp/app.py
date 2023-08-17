# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
from datetime import datetime
#################################################
# Database Setup
#################################################
print("------------------------")
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
print("+++++++++++++++++++++++++++++++++++++++++")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# IMPORTANTE VARIABLES USED IN MULTIPLE FLASK ROUTES 
#################################################
# Create our session (link) from Python to the DB
session = Session(engine)
# 1.--Find the most recent date in the data set.
rows=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
# 1.a)--getting string 
for each_row in rows:
    mrd=each_row
# 1.b)--converting string to datime
most_recent_date=datetime.strptime(mrd,'%Y-%m-%d')
# DELTA most recent date-opne year
year_ago=most_recent_date-dt.timedelta(days=366)
session.close()



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"-----------------*NOTE*---------------------<br/>"
        f"Format of start_date:YYYY-MM-dd<br/>"
        f"Format of end_date:YYYY-MM-dd<br/>"

    )


@app.route("/api/v1.0/precipitation")
def precipitations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #Query date and pcrp from the most recent date-one year
    scores=session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date>=year_ago).filter(Measurement.date<=most_recent_date)
    session.close()
    
    # Create a dictionary from the row data and append to a list 
    list_prec = []
    for date, pcrp in scores:
        precian_dict = {}
        precian_dict[date] = pcrp
        list_prec.append(precian_dict)

    return jsonify(list_prec)
#######################################################################################################################33
#######################################Station
########################################################################################################################
@app.route("/api/v1.0/stations")
def stationss():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations information
    stations_names = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()
    # Create a dictionary from the row data and append to a list
    list_stations = []
    for station, name,latitude,longitude,elevation in stations_names:
        _dict = {}
        _dict["Station"] = station
        _dict["Name"] = name
        _dict["latitude"] = latitude
        _dict["longitude"] = longitude
        _dict["elevation"] = elevation
        list_stations.append(_dict)

    return jsonify(list_stations)

#######################################################################################################################33
#######################################TOBS
########################################################################################################################
@app.route("/api/v1.0/tobs")
def tobbsd():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #find most active station    
    most_active=session.query(Measurement.station,func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    #getting station id out of touple
    for each_most in most_active:
        station_id,count_station_id=most_active
    #Getting date and tobs of most active station
    last_year_most_active=session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.station == station_id).\
            filter(Measurement.date>=year_ago).filter(Measurement.date<=most_recent_date).all()
    
    temperature=[]
    for each_y in last_year_most_active:
        temperature.append(each_y)
    temperature

    session.close()
    #
    LIST_TOBS = []
    for date, tobs in temperature:
        _dict = {}
        _dict["date"] = date
        _dict["tobs"] = tobs
        LIST_TOBS.append(_dict)
    print("Getting data from",station_id)
    return jsonify(LIST_TOBS) 
#######################################################################################################################33
#######################################Start
########################################################################################################################
@app.route("/api/v1.0/<start_date>")
def sd(start_date):

    #-------------------------------------
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # getting de start point
    # --getting query date as datetime
    url_start_date=datetime.strptime(start_date,'%Y-%m-%d')
    gettting_lha=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
         filter(Measurement.date>=url_start_date).filter(Measurement.date<=most_recent_date).all()

    # Create a dictionary from the row data and append to a list
    LIST_DES = []
    for minn, maxx,avgg in gettting_lha:
        _dict = {}
        _dict["Start date"] = url_start_date
        _dict["End date"] = most_recent_date
        _dict["min"] = minn
        _dict["max"] = maxx
        _dict["average"] = avgg
        LIST_DES.append(_dict)

    return jsonify(LIST_DES) 


#######################################################################################################################33
#######################################Start end
########################################################################################################################
@app.route("/api/v1.0/<start_date>/<end_date>")
def ed(start_date,end_date):
    #-------------------------------------
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # 1. getting de start point
    # 1.b)--getting query START TIME date as datetime
    url_start_date=datetime.strptime(start_date,'%Y-%m-%d')
    # 1.c)--getting query END TIME date as datetime
    url_end_time=datetime.strptime(end_date,'%Y-%m-%d')
    
    gettting_lha=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
         filter(Measurement.date>=url_start_date).filter(Measurement.date<=url_end_time).all()

    all_temps = list(np.ravel(gettting_lha))
    LIST_DES = []
    for minn, maxx,avgg in gettting_lha:
        _dict = {}
        _dict["Start date"] = url_start_date
        _dict["End date"] = url_end_time
        _dict["min"] = minn
        _dict["max"] = maxx
        _dict["average"] = avgg
        LIST_DES.append(_dict)

    return jsonify(LIST_DES) 



if __name__ == '__main__':
    app.run(debug=True)
