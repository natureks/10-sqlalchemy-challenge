import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
import pandas as pd

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
lst_class = Base.classes.keys()

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
        f"Available API's:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"                
        f"/api/v1.0/start"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).all()

    dates_gb = [result[0] for result in results[:]]
    precips_gb = [result[1] for result in results[:]]
    res = {} 
    for key in dates_gb: 
        for value in precips_gb: 
            res[key] = value 

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(res))

    return jsonify(all_names)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Measurement.station).group_by(Measurement.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    end_date = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date == func.max(Measurement.date).select()).first()[0]
    begin_date = (dt.datetime.strptime(end_date, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    print(f"Dates: {begin_date} {end_date}")
    
    session = Session(engine)
    results = session.query(Measurement.date, func.round(func.sum(Measurement.prcp),2))\
        .group_by(Measurement.date)\
        .filter(Measurement.date.between(begin_date, end_date))
    session.close()

    df = pd.DataFrame(results, columns=["Date", "Percp"])

    return jsonify(df.values.tolist())

@app.route("/api/v1.0/<start_date>/<end_date>")
def start(start_date, end_date):
	''' 
		http://127.0.0.1:5000/api/v1.0/2010-01-29/2010-02-09
	'''
	# Create our session (link) from Python to the DB
	session = Session(engine)

	results = session.query(func.min(Measurement.tobs),\
							func.round(func.avg(Measurement.tobs),2),\
							func.max(Measurement.tobs)).\
							filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
	session.close()

	# Convert list of tuples into normal list
	all_names = list(np.ravel(results))

	return jsonify(all_names)

@app.route("/api/v1.0/start_zz")
def start_zz():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    end_date = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date == func.max(Measurement.date).select()).first()[0]
    start_date = (dt.datetime.strptime(end_date, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    results = session.query(func.min(Measurement.tobs),\
                            func.round(func.avg(Measurement.tobs),2),\
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

if __name__ == '__main__':
    app.run(debug=False)
