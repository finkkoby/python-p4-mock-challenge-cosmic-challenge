#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Planets(Resource):
    def get(self):
        planets = [planet.to_dict(only=('id', 'name', 'distance_from_earth', 'nearest_star'))
                   for planet in Planet.query.all()]
        return planets, 200
class Scientists(Resource):
    def get(self):
        scientists = [scientist.to_dict(only=('id', 'name', 'field_of_study'))
                      for scientist in Scientist.query.all()]
        return scientists, 200
    def post(self):
        json = request.get_json()
        try:
            scientist = Scientist(
                name=json['name'],
                field_of_study=json['field_of_study']
            )
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict(), 201
        except:
            return {"errors": ["validation errors"]}, 400
class ScientistsId(Resource):
    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if scientist:
            return scientist.to_dict(), 200
        else:
            return {"error": "Scientist not found"}, 404
    def patch(self, id):
        json = request.get_json()
        try:
            scientist = Scientist.query.filter(Scientist.id == id).first()
            if scientist:
                scientist.name = json['name']
                scientist.field_of_study = json['field_of_study']
                db.session.commit()
                return scientist.to_dict(), 202
            else:
                return {"error": "Scientist not found"}, 404
        except:
            return {"errors": ["validation errors"]}, 400
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            return {}, 204
        else:
            return {"error": "Scientist not found"}, 404

class Missions(Resource):
    def post(self):
        json = request.get_json()
        try:
            mission = Mission(
                name=json['name'],
                scientist_id=json['scientist_id'],
                planet_id=json['planet_id']
            )
            db.session.add(mission)
            db.session.commit()
            return mission.to_dict(), 201
        except:
            return {"errors": ["validation errors"]}, 400

api.add_resource(Planets, '/planets')
api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistsId, '/scientists/<int:id>')
api.add_resource(Missions, '/missions')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
