"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code
# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)
@app.route('/user', methods=['GET'])
def get_user():
    all_user = User.query.all()
    results = []
    for user in all_user:
        results.append(user.serialize())
    return jsonify(results), 200
@app.route('/people', methods=['GET'])
def get_people():
    all_people = People.query.all()
    results = []
    for people in all_people:
        results.append(people.serialize())
    return jsonify(results), 200
@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_id(people_id):
    people = People.query.get(people_id)
    if People is None:
        return jsonify(), 200
    return jsonify(people.serialize()), 200
@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets = Planets.query.all()
    results = []
    for planets in all_planets:
        results.append(planets.serialize())
    return jsonify(results), 200
@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_planet_id(planets_id):
    planets= Planets.query.get(planets_id)
    if Planets is None:
        return jsonify(), 200
    return jsonify(planets.serialize()), 200
@app.route('/user/favorites', methods=['GET'])
def get_favorites():
    all_favorites = Favorites.query.all()
    results = []
    for user in all_favorites:
        results.append(user.serialize())
    return jsonify(results), 200

@app.route('/favorites/planets/<int:planet_id>', methods=['POST'])
def create_favorites_planets(planet_id):
    body = request.get_json()
    new_planet = Planets(
        id=body.get('id'),
        name=body.get('name'),
        climate=body.get('climate'),
        terrain=body.get('terrain'),
        population=body.get('population')
    )

    db.session.add(new_planet)
    db.session.commit()

    return jsonify(new_planet.serialize()), 200

@app.route('/user', methods=['POST'])
def create_user():
    body = request.get_json()
    new_user = User(
        id=body['id'],
        email=body['email'],
        password=body['password'],
        first_name=body['first_name'],
        last_name=body['last_name']
    )


    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.serialize()), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)