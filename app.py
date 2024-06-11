from flask import Flask

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
    a = session.query(AirportsData).order_by(AirportsData.airport_code)
    return [{"code": i.airport_code, "name": i.airport_name["en"]} for i in a]


if __name__ == '__main__':
    app.run()
