__author__ = 'shubham'

import os
from flask import Flask, json, request, g, Response
from flask.ext.restful import Resource, Api
import MySQLdb as mdb
import sys
import collections
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
app = Flask(__name__)
api = Api(app)


class RestaurantLocater(Resource):
    def __init__(self):
        self.con = mdb.connect('localhost', 'admin', '', 'latlang');
        self.cur = self.con.cursor()

    def get_names(self, lat, long):
        self.cur.execute("SELECT outlet_name, address_line, m_m, "
                         "SQRT(POW(69.1 * (latitude - %s), 2) + POW(69.1 * (%s - longitude) * COS(latitude / 57.3), 2)) "
                         "AS distance FROM restaurants "
                         "HAVING distance < 5 ORDER BY distance;", (lat, long))

        rows = self.cur.fetchall()
        return rows


def get_restaurants():
    g.Restaurant_Locater = RestaurantLocater()
    return g.Restaurant_Locater


@app.route('/latlong', methods=['POST'])
def post():
    latlong = request.data

    latlong = latlong.split(',')
    lat = latlong[0]
    long = latlong[1]

    name_instance = get_restaurants()
    names = name_instance.get_names(lat, long)

    objects_list = []
    for row in names:
        d = collections.OrderedDict()
        d['outlet_name'] = row[0]
        d['address_line1'] = row[1]
        d['address_line2'] = row[2]
        d['distance'] = row[3]
        objects_list.append(d)

    j = json.dumps(objects_list)
    print j
    resp = Response(j, status=200, mimetype='application/json')

    return resp

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
