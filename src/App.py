import os

from bson import ObjectId
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)

db_url = os.getenv("DATABASE_URL")
db_name = os.getenv("DATABASE")

# Connessione a MongoDB
client = MongoClient(db_url)
db = client[db_name]
collection = db['data']
xy_collection = db['history']  # Collezione per lo storico delle coppie x, y
test_data_coll = db['test_data']
ssid_coll = db['ssid']

app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET")
jwt = JWTManager(app)

users = {
    os.getenv("USERNAME"): os.getenv("PASSWORD")
}


@app.route('/data', methods=['POST'])
@jwt_required()
def add_data():
    incoming_data = request.json
    if not incoming_data or 'x' not in incoming_data or 'y' not in incoming_data or 'data' not in incoming_data or 'date' not in incoming_data:
        return jsonify({'error': 'Invalid data format'}), 400

    x = incoming_data['x']
    y = incoming_data['y']
    data_list = incoming_data['data']
    date = incoming_data['date']

    # Cerca se esiste già un documento con la stessa coppia (x, y) e la stessa data
    query = {'x': x, 'y': y, 'date': date}
    existing_record = collection.find_one(query)

    if existing_record:
        # Aggiungi i nuovi dati alla lista esistente
        collection.update_one(query, {'$push': {'data': {'$each': data_list}}})
    else:
        # Crea un nuovo documento se non esiste
        new_record = {'x': x, 'y': y, 'data': data_list, 'date': date}
        collection.insert_one(new_record)

        # Aggiungi la nuova coppia (x, y) nella collezione storico
        if not xy_collection.find_one({'x': x, 'y': y}):
            xy_collection.insert_one({'x': x, 'y': y})

    return jsonify({'message': 'Data processed successfully'}), 201


@app.route('/data', methods=['DELETE'])
@jwt_required()
def remove_data_by_id():
    incoming_data = request.json
    if not incoming_data or 'id' not in incoming_data:
        return jsonify({'error': 'Invalid data format'}), 400

    record_id = incoming_data['id']
    query = {'_id': record_id}
    result = collection.delete_one(query)

    if result.deleted_count:
        return jsonify({'message': 'Data removed successfully'}), 200
    return jsonify({'message': 'No data found'}), 404


@app.route('/data', methods=['PUT'])
@jwt_required()
def update_data_by_id():
    incoming_data = request.json
    if not incoming_data or 'id' not in incoming_data:
        return jsonify({'error': 'Invalid data format'}), 400

    id_ = incoming_data['id']
    id_ = ObjectId(id_)
    query = {'_id': id_}

    result = collection.find_one(query)

    if not result:
        return jsonify({'message': 'No data found'}), 404

    new_values = {'$set': {}}
    if "x" in incoming_data:
        x = incoming_data['x']
        new_values['$set']['x'] = x
    if "y" in incoming_data:
        y = incoming_data['y']
        new_values['$set']['y'] = y
    if "data" in incoming_data:
        data_list = incoming_data['data']
        new_values['$set']['data'] = data_list
    if "date" in incoming_data:
        date = incoming_data['date']
        new_values['$set']['date'] = date

    try:
        result = collection.update_one(query, new_values)
        return jsonify({'message': 'Data updated successfully', 'data': result.raw_result, 'query': new_values}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/data/test', methods=['POST'])
@jwt_required()
def add_test_data():
    incoming_data = request.json
    if 'RP' not in incoming_data or 'data' not in incoming_data:
        return jsonify({'error': 'Invalid data format'}), 400

    data_list = incoming_data['data']
    rp = incoming_data['RP']

    # Crea un nuovo documento se non esiste
    new_record = {'data': data_list, 'RP': rp}
    test_data_coll.insert_one(new_record)

    return jsonify({'message': 'Data processed successfully'}), 201


@app.route('/data/test', methods=['GET'])
def get_test_data():
    results = test_data_coll.find()
    if not results:
        return jsonify({'message': 'No data found'}), 404
    return dumps(results), 200


@app.route('/data', methods=['GET'])
def get_data():
    results = collection.find()
    if not results:
        return jsonify({'message': 'No data found'}), 404
    return dumps(results), 200


@app.route('/data/space/coordinates', methods=['GET'])
def get_coordinates_history():
    # Restituisce tutte le coppie uniche di x, y
    results = xy_collection.find()
    if not results:
        return jsonify({'message': 'No data found'}), 404
    return dumps(results), 200


# Endpoint dove riceve json con { "ssid": "ssid", "type": "A" }
@app.route('/data/ssid', methods=['POST'])
@jwt_required()
def add_ssid():
    incoming_data = request.json
    if not incoming_data or 'ssid' not in incoming_data or 'type' not in incoming_data:
        return jsonify({'error': 'Invalid data format'}), 400

    ssid = incoming_data['ssid']
    type = incoming_data['type']

    # Cerca se esiste già un documento con lo stesso ssid e type
    query = {'ssid': ssid}
    existing_record = ssid_coll.find_one(query)

    # Se il documento esiste già aggiorna il tip

    if existing_record:
        # Aggiungi i nuovi dati alla lista esistente
        ssid_coll.update_one(query, {'$set': {'type': type}})
    else:
        # Crea un nuovo documento se non esiste
        new_record = {'ssid': ssid, 'type': type}
        ssid_coll.insert_one(new_record)

    return jsonify({'message': 'Data processed successfully'}), 201


@app.route('/data/ssid', methods=['DELETE'])
@jwt_required()
def remove_ssid():
    incoming_data = request.json
    if not incoming_data or 'ssid' not in incoming_data:
        return jsonify({'error': 'Invalid data format'}), 400

    ssid = incoming_data['ssid']
    query = {'ssid': ssid}
    result = ssid_coll.delete_one(query)

    if result.deleted_count:
        return jsonify({'message': 'Data removed successfully'}), 200
    return jsonify({'message': 'No data found'}), 404


# Get all ssid
@app.route('/data/ssid', methods=['GET'])
@jwt_required()
def get_ssid():
    results = ssid_coll.find()
    if not results:
        return jsonify({'message': 'No data found'}), 404
    return dumps(results), 200


if __name__ == '__main__':
    app.run(debug=True)
