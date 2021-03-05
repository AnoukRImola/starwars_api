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
from models import db, Usuario, Personaje, Planeta, Favoritos
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
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


@app.route('/personaje', methods=['GET'])
def get_personajes():
    personas = Personaje.query.all()
    result = list(map(lambda x: x.serialize(), personas))

    return jsonify(result), 200


@app.route('/personaje/<int:personaje_id>', methods=['GET'])
def get_personaje(personaje_id):
    persona = Personaje.query.get(personaje_id) 

    if persona is None:
        raise APIException("El personaje no esta registardo", status_code=404)   
    result = persona.serialize_personaje()

    return jsonify(result), 200


@app.route('/planeta', methods=['GET'])
def get_planets():
    planetas = Planeta.query.all()
    result = list(map(lambda x: x.serialize(), planetas))

    return jsonify(result), 200



@app.route('/planeta/<int:planeta_id>', methods=['GET'])
def get_planet(planeta_id):
    planeta = Planeta.query.get(planeta_id) 

    if planeta is None:
        raise APIException("El planeta no esta registardo", status_code=404)   
    result = planeta.serialize()

    return jsonify(result), 200
    

@app.route('/usuario', methods=['GET'])
def get_usuario():
    user = Usuario.query.all()
    result = list(map(lambda x: x.serialize(), user))

    return jsonify(result), 200


@app.route('/usuario/<int:usuario_id>/favoritos', methods=['GET'])
def get_favoritos(usuario_id):
    favorits = Favoritos.query.filter_by(usuario_id=usuario_id) 

    if favorits is None:
        raise APIException("El favorito no esta registrado", status_code=404)   
    result = list(map(lambda x: x.serialize(), favorits))

    return jsonify(result), 200      


@app.route('/add_favoritos/<int:usuario_id>', methods=['POST'])
def add_fav(usuario_id):

    request_body = request.get_json()
    favori = Favoritos(planeta_name=request_body["planeta_name"], personaje_name=request_body['personaje_name'])
    db.session.add(favori)
    db.session.commit()

    return jsonify("Favorito agregado"), 200    


@app.route('/del_favoritos/<int:favoritos_id>', methods=['DELETE'])
def del_fav(favoritos_id):
    
    fav = Favoritos.query.get(favoritos_id)

    if fav is None:
        raise APIException('Favorito no encontrado', status_code=404)

    db.session.delete(fav)

    db.session.commit()

    return jsonify("Eliminado"), 200    




# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
