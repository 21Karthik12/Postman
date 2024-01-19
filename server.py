from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import secrets


app = Flask(__name__)
CORS(app)


users = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/addMovie', methods=['POST'])
def add_movie():
    global users
    request_data = request.get_json()
    request_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_id = secrets.token_hex(15)
    users[user_id] = request_data
    return jsonify({'id': user_id})


@app.route('/getAllMovies', methods=['GET'])
def get_all_movies():
    global users
    return jsonify([{'id': id, **user} for id, user in users.items()])


@app.route('/getOneMovie/<id>', methods=['GET'])
def get_one_movie(id):
    global users
    if id in users.keys():
        user = users[id]
        user['id'] = id
        return jsonify(user)
    return jsonify({'error': 'ID not found'}), 404


@app.route('/deleteMovie/<id>', methods=['DELETE'])
def delete_movie(id):
    global users
    result = users.pop(id, None)
    if result is not None:
        return jsonify({'message': 'User deleted successfully'})
    return jsonify({'error': 'ID not found'}), 404


@app.route('/updateMovie/<id>', methods=['PUT'])
def update_movie(id):
    global users
    request_data = request.get_json()
    request_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if id in users.keys():
        users[id] = request_data
        return jsonify({'message': 'User updated successfully'})
    return jsonify({'error': 'User not found'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
