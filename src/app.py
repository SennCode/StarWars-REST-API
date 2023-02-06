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
from models import db, User
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

# Listar todos los registros de people en la base de datos

@app.route('/people', methods=['GET'])
def people():
    all_people = People.query.all()
    all_people = list(map(lambda person: person.serialize(), all_people))
    
    return jsonify({all_people}), 200

# Listar la información de una sola people

@app.route('/people/<int:people_id>', methods=['GET'])
def person():
    one_person = People.query.filter_by(people_id = people_id)
    
    return jsonify({one_person.serialize()}), 201

# Listar los registros de planets en la base de datos

@app.route('/planets', methods=['GET'])
def planets():
    all_planets = Planets.query.all()
    all_planets = list(map(lambda planet: planet.serialize(), all_planets))

    return jsonify({all_planets}), 200

# Listar la información de un solo planet

@app.route('/planets/<int:planet_id', methods=['GET'])
def planet():
    one_planet = Planets.query.filter_by(planet_id = planet_id)

    return jsonify({one_planet.serialize()}), 201

# Listar todos los usuarios del blog

@app.route('/users', methods=['GET'])
def users():
    all_users = Users.query.all()
    all_users = list(map(lambda user: user.serialize(), all_users))

    return jsonify({all_users}), 200

# Listar todos los favoritos que pertenecen al usuario actual.

@app.route('/users/favorites', methods=['GET'])
def users_favorites():
    favorites = Users.query.get('favorites', None)
    favorites = list(map(lambda favorite: favorite.serialize(), favorites))

    return jsonify({favorites}), 200

# Añade un nuevo planet favorito al usuario actual con el planet id = planet_id.

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    # SE COMPRUEBA QUE EXISTE EL USUARIO Y PLANET
    user = User.query.filter_by(user_id = user_id)
    if not user:
        return jsonify ({"msg": "El usuario no existe"}), 400
    one_planet = Planet.query.filter(planet_id = planet_id)
    if not planet:
        return jsonify ({"msg": "El planeta no existe"}), 400
# SE ASIGNAN LOS VALORES AL FAVORITO QUE DESEAMOS AÑADIR DETERMINANDO EL ID DEL USUARIO Y EL ID DE PLANET
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    # AQUI SE AÑADE Y SE GUARDA LA INFO
    db.session.add(favorite)
    db.session.commit()

    return "El planeta ha sido añadido a favoritos", 201

# Añade una nueva people favorita al usuario actual con el people.id = people_id.

@app.route('/favorite/people/<int:people_id>', methods=["POST"])
def add_favorite_people(people_id):
    # SE COMPRUEBA QUE EXISTE EL USUARIO Y PEOPLE
    user = User.query.filter_by(user_id = user_id)
    if not user: 
        return ({"msg": "El usuario no existe!"}), 400
    one_person = People.query.filter_by(people_id = people_id)
    if not one_person:
        return ({"msg": "La persona no existe!"}), 400
    # SE ASIGNAN LOS VALORES AL FAVORITO QUE DESEAMOS AÑADIR DETERMINANDO EL ID DEL USUARIO Y EL ID DE PEOPLE
    favorite = Favorite(user_id=user_id, people_id=people_id)
    # AQUI SE AÑADE Y SE GUARDA LA INFO
    db.session.add(favorite)
    db.session.commit()

    return ({"msg": "La persona ha sido añadida a favoritos"}), 201

# Elimina un planet favorito con el id = planet_id`.

@app.route('/favorite/planet/<int:planet_id>', methods=["DELETE"])
def remove_favorite_planet(planet_id):
    # SE COMPRUEBA QUE EXISTE EL USUARIO Y PLANET
    user = User.query.filter_by(user_id = user_id)
    if not user:
        return ({"msg": "El usuario no existe!"}), 400
    one_planet = Planets.query.filter_by(planet_id = planet_id)
    if not planet:
        return jsonify ({"msg": "El planeta no existe!"}), 400
    if planet not in user.favorite_planets:
        return jsonify({"msg": "Planet no está en favoritos!"}), 400
    # SE ASIGNAN LOS VALORES AL FAVORITO QUE DESEAMOS BORRAR DETERMINANDO EL ID DEL USUARIO Y EL ID DE PLANET
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    # AQUI SE BORRA Y SE GUARDA LA INFO
    db.session.delete(favorite)
    db.session.commit()

    return ({"msg": "El planeta ha sido borrado de favoritos!"})

# Elimina una people favorita con el id = people_id

@app.route('/favorite/people/<int:people_id>', methods=["DELETE"])
def remove_favorite_people(people_id):
    # SE COMPRUEBA QUE EXISTE EL USUARIO Y PEOPLE
    user = User.query.filter_by(user_id=user_id)
    if not user:
        return ({"masg": "El usuario no existe!"})
    one_person = People.query.filter_by(people_id=people_id)
    if not one_person:
        return ({"msg": "La persona no existe!"})
    # SE ASIGNAN LOS VALORES AL FAVORITO QUE DESEAMOS BORRAR DETERMINANDO EL ID DEL USUARIO Y EL ID DE PEOPLE
    favorite = Favorite(user_id=user_id, people_id=people_id)
    # AQUI SE BORRA Y SE GUARDA LA INFO
    db.session.delete(favorite)
    db.session.commit()

    return ({"msg": "La persona ha sido eliminada de favoritos!"})


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
