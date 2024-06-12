from flask import Flask, abort

from db import db_session
from db.table import *

app = Flask(__name__)
db_session.global_init()


@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/cities', methods=['GET'])
def cities():
    session = db_session.create_session()
    a = session.query(AirportsData.city).distinct().order_by(AirportsData.city)
    return [i[0]["en"] for i in a]


@app.route('/airports', methods=['GET'])
def airports():
    session = db_session.create_session()
    a = session.query(AirportsData).order_by(AirportsData.city)
    return [{"city": i.city, "code": i.airport_code, "name": i.airport_name["en"]} for i in a]


@app.route('/airports/<city>', methods=['GET'])
def airports_city(city):
    session = db_session.create_session()
    a = session.query(AirportsData).filter(AirportsData.city['en'].astext.like(city))
    if a.count() == 0:
        abort(404)
    return [{"code": i.airport_code, "name": i.airport_name["en"]} for i in a.order_by(AirportsData.airport_code)]


@app.route('/outbound/<airport>', methods=['GET'])
def outbound(airport):
    session = db_session.create_session()
    a = session.query(t_schedule_routes).filter(t_schedule_routes.columns.departure_airport.like(airport))
    if a.count() == 0:
        abort(404)
    return [{
        "flight_no": i.flight_no,
        "arrival_airport": i.arrival_airport,
        "departure_time": i.scheduled_departure,
        "days_of_week": i.days_of_week,
    } for i in a]


@app.route('/inbound/<airport>', methods=['GET'])
def inbound(airport):
    session = db_session.create_session()
    a = session.query(t_schedule_routes).filter(t_schedule_routes.columns.arrival_airport.like(airport))
    if a.count() == 0:
        abort(404)
    return [{
        "flight_no": i.flight_no,
        "departure_airport": i.departure_airport,
        "arrival_time": i.scheduled_arrival,
        "days_of_week": i.days_of_week,
    } for i in a]


if __name__ == '__main__':
    app.run()
