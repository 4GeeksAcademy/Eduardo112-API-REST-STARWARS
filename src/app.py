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
from models import db, User, Character, Planet, FavoritesList
from datetime import datetime

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
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }
    return jsonify(response_body), 200

# GET ALL USERS
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()            #query = consulta
    return jsonify([user.serialize() for user in users]), 200

# GET PEOPLE_ID
@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_character(people_id):   
    character = Character.query.filter_by(id=people_id).first()   # first el primero que encuentre me lo devuelve.
                #en la tabla Character buscamos por filtro que id sea = a people_id, people_id es el numero que nos manda el usuario. 
    if not character:
        return jsonify({"message": "Personaje no existe"}), 404
    return jsonify(character.serialize()), 200
    
#GET ALL PLANET
@app.route('/planet', methods=['GET'])
def get_all_planet():
    planets = Planet.query.all()            #query = consulta
    return jsonify([planet.serialize() for planet in planets]), 200

#GET PLANET_ID
@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):   
    planet = Planet.query.filter_by(id=planet_id).first()   # first el primero que encuentre me lo devuelve.
                #en la tabla Character buscamos por filtro que id sea = a people_id, people_id es el numero que nos manda el usuario. 
    if not planet:
        return jsonify({"message": "Planeta no existe"}), 404
    return jsonify(planet.serialize()), 200

#POST PLANET
@app.route('/planet', methods=['POST'])
def create_planet():
    data = request.get_json()
    new_planet = Planet(
        name = data.get("name"),
        size = data.get("size"),
        climate = data.get("climate"),
        population = data.get("population"),
    )
    db.session.add(new_planet)  # asi se prepara para agregarlo en la tabla (como un git add)
    db.session.commit()    # así se guarda en la tabla

    return jsonify(new_planet.serialize()), 201

# POST CHARACTER
@app.route('/people', methods=['POST'])
def create_character():
    data = request.get_json()
    new_character =  Character(
        name = data.get("name"),
        species = data.get("species"),
        gender = data.get("gender"),
    )
    db.session.add(new_character)  # asi se prepara para agregarlo en la tabla (como un git add)
    db.session.commit()    # así se guarda en la tabla

    return jsonify(new_character.serialize()), 201

# GET ALL CHARACTER
@app.route('/people', methods=['GET'])
def get_all_characters():
    characters = Character.query.all()            #query = consulta
    return jsonify([character.serialize() for character in characters]), 200

# AGREGAR UN CHARACTER A FAVORITO 
@app.route('/favorite/character/<int:user_id>/<int:character_id>', methods=['POST'])
def add_character_favorite(user_id, character_id):
    if not user_id:      
        raise APIException("user_id requerido")

    character = Character.query.get(character_id)
    if not character:
        raise APIException("Personaje no encontrado", 400)

    existe = FavoritesList.query.filter_by(user_id=user_id, character_id=character_id).first()
    if existe:
        return jsonify({"message": "Personaje ya está en favoritos"}), 200

    favorito = FavoritesList(user_id=user_id, character_id=character_id)
    db.session.add(favorito)
    db.session.commit()

    return jsonify(favorito.serialize()), 201

# POST DE PLANET A FAVORITE
@app.route('/favorite/planet/<int:user_id>/<int:planet_id>', methods=['POST'])
def add_planet_favorite(user_id, planet_id):
    if not user_id:      
        raise APIException("user_id requerido")

    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException("Planeta no encontrado", 400)

    existe = FavoritesList.query.filter_by(user_id=user_id, planet_id=planet_id).first()  #busca con el query y filtra por userid y planeta y el .first es el primero que encuentra (la primera coincidencia).
    if existe:
        return jsonify({"message": "Planeta ya está en favoritos"}), 200

    favorito = FavoritesList(user_id=user_id, planet_id = planet_id)  #planet_id = planet_id el primero es si esta en la columna (que el del codigo del models) de la base de datos, el segundo es el parametro que meto como variable en el endpoint. 
    db.session.add(favorito)
    db.session.commit()

    return jsonify(favorito.serialize()), 201

#DELETE DE PLANET
@app.route('/favorite/planet/<int:user_id>/<int:planet_id>', methods=['DELETE'])
def delete_planet_favorite(user_id, planet_id):
    existe = FavoritesList.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not existe:
        return jsonify({"message": "Favorito de planeta no encontrado"}), 404

    db.session.delete(existe)
    db.session.commit()
    return jsonify({"message": "Favorito de planeta eliminado"}), 204

#DELETE DE CHARACTER
@app.route('/favorite/people/<int:user_id>/<int:people_id>', methods=['DELETE'])
def delete_character_favorite(user_id, people_id):
    existe = FavoritesList.query.filter_by(user_id=user_id, character_id=people_id).first()
    if not existe:
        return jsonify({"message": "Favorito de planeta no encontrado"}), 404

    db.session.delete(existe)
    db.session.commit()
    return jsonify({"message": "Favorito de planeta eliminado"}), 204


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
