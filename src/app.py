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
from models import db, User, Planet, Character, FavoriteCharacter, FavoritePlanet
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

# =============== ENDPOINTS =============== #

# ========== get users ========== #
@app.route('/users', methods=['GET'])
def get_users():
    users_query = User.query.all()
    serialized_users = list(map(lambda item: item.serialize(), users_query))

    response_body = {
         "msg": "ok",
         "total_users": len(serialized_users),
         "result": serialized_users
     }
    
    return jsonify(response_body), 200


# ========== get user by id ========== #
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user_query = User.query.get(user_id)

    if user_query is None:
        return jsonify({"msg": f"El usuario con id {user_id} no existe"}), 404
    else:
        return jsonify(user_query.serialize()), 200


# ========== get planets ========== #
@app.route('/planets', methods=['GET'])
def get_planets():
    planets_query = Planet.query.all()
    serialized_planets = list(map(lambda item: item.serialize(), planets_query))

    response_body = {
        "msg": "ok",
        "total_planets": len(serialized_planets),
        "result": serialized_planets
    }

    return jsonify(response_body), 200


# ========== get planet by id ========== #
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet_query = Planet.query.get(planet_id)

    if planet_query is None:
        return jsonify({"msg": f"El planeta con id {planet_id} no existe"}), 404
    else:
        return jsonify(planet_query.serialize()), 200
    

# ========== get characters ========== #
@app.route('/characters', methods=['GET'])
def get_characters():
    characters_query = Character.query.all()
    serialized_characters = list(map(lambda item: item.serialize(), characters_query))

    response_body = {
        "msg": "ok",
        "total_characters": len(serialized_characters),
        "result": serialized_characters
    }

    return jsonify(response_body), 200


# ========== get character by id ========== #
@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character_query = Character.query.get(character_id)

    if character_query is None:
        return jsonify({"msg": f"El personaje con id {character_id} no existe"}), 404
    else:
        return jsonify(character_query.serialize()), 200


# ========== get favorites by user id ========== #
@app.route('/favorites/<int:user_id>', methods=['GET'])
def get_favorites_by_user(user_id):
    user = User.query.get(user_id)

    if user is None:
        return jsonify({"msg": f"El usuario con id {user_id} no existe"}), 404
    
    # Usando la relación
    favorite_characters_query = FavoriteCharacter.query.filter_by(user_id=user_id)
    serialized_favorite_characters = list(map(lambda item: item.serialize()['character'], favorite_characters_query))

    # Usando un join
    favorite_planets_query = db.session.query(FavoritePlanet, Planet).join(Planet).filter(FavoritePlanet.user_id == user_id).all()
    serialized_favorite_planets = []
    for favorite_item, planet_item in favorite_planets_query:
        serialized_favorite_planets.append(planet_item.serialize())

    response_body = {
        "msg": "ok",
        "total_favorites": len(serialized_favorite_characters) + len(serialized_favorite_planets),
        "result": {
            "favorite_characters": serialized_favorite_characters,
            "favorite_planets": serialized_favorite_planets
        }
    }

    return jsonify(response_body), 200


# ========== post favorite planet ========== #
@app.route('/favorites/planets', methods=['POST'])
def add_favorite_planet():
    request_body = request.get_json(silent=True)

    # Chequear si la petición trajo datos en el body
    if request_body is not None: 
        print("Incoming request with the following body", request_body)
    else:
        return jsonify({"msg": f"Error: la petición no incluye datos en el body"}), 400

    # Chequear si el body trae los datos correctos del usuario
    if request_body.get('user_id') is not None:
        user_query = User.query.get(request_body['user_id'])

        if user_query is None:
            return jsonify({"msg": f"El usuario con id {request_body['user_id']} no existe."}), 400
        
    else:
        return jsonify({"msg": f"Error: el body de la petición no incluye la propiedad user_id"}), 400
    
    # Chequear si el body trae los datos correctos del planeta
    if request_body.get('planet_id') is not None:
        planet_query = Planet.query.get(request_body['planet_id'])

        if planet_query is None:
            return jsonify({"msg": f"El planeta con id {request_body['planet_id']} no existe."}), 400
        
    else:
        return jsonify({"msg": f"Error: el body de la petición no incluye la propiedad planet_id"}), 400
     
    # Crear el diccionario con los datos de la petición
    favorite_planet = FavoritePlanet()
    favorite_planet.user_id = request_body['user_id']
    favorite_planet.planet_id = request_body['planet_id']
    # Insertar un registro mediante el diccionario
    db.session.add(favorite_planet)
    # Guardar los cambios realizados en la BD
    db.session.commit()

    # Devolver al frontend la lista de favoritos del usuario actualizada
    favorite_characters_query = FavoriteCharacter.query.filter_by(user_id = request_body['user_id'])
    serialized_favorite_characters = list(map(lambda item: item.serialize()['character'], favorite_characters_query))

    favorite_planets_query = FavoritePlanet.query.filter_by(user_id = request_body['user_id'])
    serialized_favorite_planets = list(map(lambda item: item.serialize()['planet'], favorite_planets_query))

    response_body = {
        "msg": "ok",
        "total_favorites": len(serialized_favorite_characters) + len(serialized_favorite_planets),
        "result": {
            "favorite_characters": serialized_favorite_characters,
            "favorite_planets": serialized_favorite_planets
        }
    }

    return jsonify(response_body), 200


# ========== post favorite character ========== #
@app.route('/favorites/characters', methods=['POST'])
def add_favorite_character():
    request_body = request.get_json(silent=True)

    # Chequear si la petición trajo datos en el body
    if request_body is not None: 
        print("Incoming request with the following body", request_body)
    else:
        return jsonify({"msg": f"Error: la petición no incluye datos en el body"}), 400

    # Chequear si el body trae los datos correctos del usuario
    if request_body.get('user_id') is not None:
        user_query = User.query.get(request_body['user_id'])

        if user_query is None:
            return jsonify({"msg": f"El usuario con id {request_body['user_id']} no existe."}), 400
        
    else:
        return jsonify({"msg": f"Error: el body de la petición no incluye la propiedad user_id"}), 400
    
    # Chequear si el body trae los datos correctos del personaje
    if request_body.get('character_id') is not None:
        character_query = Character.query.get(request_body['character_id'])

        if character_query is None:
            return jsonify({"msg": f"El personaje con id {request_body['character_id']} no existe."}), 400
        
    else:
        return jsonify({"msg": f"Error: el body de la petición no incluye la propiedad character_id"}), 400
     
    # Crear el diccionario con los datos de la petición
    favorite_character = FavoriteCharacter()
    favorite_character.user_id = request_body['user_id']
    favorite_character.character_id = request_body['character_id']
    # Insertar un registro mediante el diccionario
    db.session.add(favorite_character)
    # Guardar los cambios realizados en la BD
    db.session.commit()

    # Devolver al frontend la lista de favoritos del usuario actualizada
    favorite_characters_query = FavoriteCharacter.query.filter_by(user_id = request_body['user_id'])
    serialized_favorite_characters = list(map(lambda item: item.serialize()['character'], favorite_characters_query))

    favorite_planets_query = FavoritePlanet.query.filter_by(user_id = request_body['user_id'])
    serialized_favorite_planets = list(map(lambda item: item.serialize()['planet'], favorite_planets_query))

    response_body = {
        "msg": "ok",
        "total_favorites": len(serialized_favorite_characters) + len(serialized_favorite_planets),
        "result": {
            "favorite_characters": serialized_favorite_characters,
            "favorite_planets": serialized_favorite_planets
        }
    }

    return jsonify(response_body), 200


# ========== delete favorite planet ========== #
@app.route('/favorites/planets', methods=['DELETE'])
def delete_favorite_planet():
    request_body = request.get_json(silent=True)

    # Chequear si la petición trajo datos en el body
    if request_body is not None: 
        print("Incoming request with the following body", request_body)
    else:
        return jsonify({"msg": f"Error: la petición no incluye datos en el body"}), 400

    # Chequear si el body trae los datos correctos del usuario
    if request_body.get('user_id') is not None:
        user_query = User.query.get(request_body['user_id'])

        if user_query is None:
            return jsonify({"msg": f"El usuario con id {request_body['user_id']} no existe."}), 400
        
    else:
        return jsonify({"msg": f"Error: el body de la petición no incluye la propiedad user_id"}), 400
    
    # Chequear si el body trae los datos correctos del planeta
    if request_body.get('planet_id') is not None:
        planet_query = Planet.query.get(request_body['planet_id'])

        if planet_query is None:
            return jsonify({"msg": f"El planeta con id {request_body['planet_id']} no existe."}), 400
        
    else:
        return jsonify({"msg": f"Error: el body de la petición no incluye la propiedad planet_id"}), 400
     
    # Obtener el registro a eliminar
    favorite_planet = FavoritePlanet.query.filter_by(user_id = request_body['user_id'], planet_id = request_body['planet_id']).first()

    if favorite_planet is not None:
        # Eliminar el registro
        db.session.delete(favorite_planet)
        # Guardar los cambios realizados en la BD
        db.session.commit()
    else:
        return jsonify({"msg": f"El planeta con id {request_body['planet_id']} no está incluido en los favoritos del usuario con id {request_body['user_id']}."})

    # Devolver al frontend la lista de favoritos del usuario actualizada
    favorite_characters_query = FavoriteCharacter.query.filter_by(user_id = request_body['user_id'])
    serialized_favorite_characters = list(map(lambda item: item.serialize()['character'], favorite_characters_query))

    favorite_planets_query = FavoritePlanet.query.filter_by(user_id = request_body['user_id'])
    serialized_favorite_planets = list(map(lambda item: item.serialize()['planet'], favorite_planets_query))

    response_body = {
        "msg": "ok",
        "total_favorites": len(serialized_favorite_characters) + len(serialized_favorite_planets),
        "result": {
            "favorite_characters": serialized_favorite_characters,
            "favorite_planets": serialized_favorite_planets
        }
    }

    return jsonify(response_body), 200


# ========== delete favorite character ========== #
@app.route('/favorites/characters', methods=['DELETE'])
def delete_favorite_character():
    request_body = request.get_json(silent=True)

    # Chequear si la petición trajo datos en el body
    if request_body is not None: 
        print("Incoming request with the following body", request_body)
    else:
        return jsonify({"msg": f"Error: la petición no incluye datos en el body"}), 400

    # Chequear si el body trae los datos correctos del usuario
    if request_body.get('user_id') is not None:
        user_query = User.query.get(request_body['user_id'])

        if user_query is None:
            return jsonify({"msg": f"El usuario con id {request_body['user_id']} no existe."}), 400
        
    else:
        return jsonify({"msg": f"Error: el body de la petición no incluye la propiedad user_id"}), 400
    
    # Chequear si el body trae los datos correctos del personaje
    if request_body.get('character_id') is not None:
        character_query = Character.query.get(request_body['character_id'])

        if character_query is None:
            return jsonify({"msg": f"El personaje con id {request_body['character_id']} no existe."}), 400
        
    else:
        return jsonify({"msg": f"Error: el body de la petición no incluye la propiedad character_id"}), 400
     
    # Obtener el registro a eliminar
    favorite_character = FavoriteCharacter.query.filter_by(user_id = request_body['user_id'], character_id = request_body['character_id']).first()
    
    if favorite_character is not None:
        # Eliminar el registro
        db.session.delete(favorite_character)
        # Guardar los cambios realizados en la BD
        db.session.commit()
    else:
        return jsonify({"msg": f"El personaje con id {request_body['character_id']} no está incluido en los favoritos del usuario con id {request_body['user_id']}."})


    # Devolver al frontend la lista de favoritos del usuario actualizada
    favorite_characters_query = FavoriteCharacter.query.filter_by(user_id = request_body['user_id'])
    serialized_favorite_characters = list(map(lambda item: item.serialize()['character'], favorite_characters_query))

    favorite_planets_query = FavoritePlanet.query.filter_by(user_id = request_body['user_id'])
    serialized_favorite_planets = list(map(lambda item: item.serialize()['planet'], favorite_planets_query))

    response_body = {
        "msg": "ok",
        "total_favorites": len(serialized_favorite_characters) + len(serialized_favorite_planets),
        "result": {
            "favorite_characters": serialized_favorite_characters,
            "favorite_planets": serialized_favorite_planets
        }
    }

    return jsonify(response_body), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
