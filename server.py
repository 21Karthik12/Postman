from flask import Flask, render_template, request, jsonify
import flask_socketio
from flask_cors import CORS
from datetime import datetime
import secrets


app = Flask(__name__)
CORS(app)
server = flask_socketio.SocketIO(app, cors_allowed_origins="*")


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
    return jsonify(list(users.values()))


@app.route('/getOneMovie/<id>', methods=['GET'])
def get_one_movie(id):
    global users
    if id in users.keys():
        user = users[id]
        return jsonify(user)
    return jsonify({'error': 'ID not found'}), 404


@app.route('/deleteMovie/<id>', methods=['GET', 'POST'])
def delete_movie(id):
    global users
    result = users.pop(id, None)
    if result is not None:
        return jsonify({'message': 'User deleted successfully'})
    return jsonify({'error': 'ID not found'}), 404


@app.route('/updateMovie/<id>', methods=['POST'])
def update_movie(id):
    global users
    request_data = request.get_json()
    request_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if id in users.keys():
        users[id] = request_data
        return jsonify({'message': 'User updated successfully'})
    return jsonify({'error': 'User not found'}), 404


@server.on('connect', namespace='/')
def handle_connect():
    print('Frontend connected')


@server.on('disconnect', namespace='/')
def handle_disconnect():
    print('Frontend disconnected')


@server.on('json_message', namespace='/')
def handle_json_message(data):
    print('JSON Message:', data)
    server.emit('json_response', {
                'response': 'Received your JSON message'}, namespace='/')
    server.emit('json', data, namespace='/')


@server.on('json_response', namespace='/')
def handle_json_response(data):
    print('JSON Response:', data)


if __name__ == '__main__':
    server.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
