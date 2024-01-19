from flask import Flask, render_template, request, jsonify
import flask_socketio
from flask_cors import CORS
import requests
from datetime import datetime
from flask_pymongo import PyMongo
from bson import ObjectId


uri = "mongodb+srv://21karthik1202:<password>@cluster0.izvmntj.mongodb.net/movie_database?retryWrites=true&w=majority"

app = Flask(__name__)
app.config['MONGO_URI'] = uri
CORS(app)
server = flask_socketio.SocketIO(app, cors_allowed_origins="*")
mongo = PyMongo(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/addMovie', methods=['POST'])
def add_movie():
    request_data = request.get_json()
    request_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result = mongo.db.movies.insert_one(request_data)
    return jsonify({'id': str(result.inserted_id)})


@app.route('/getAllMovies', methods=['GET'])
def get_all_movies():
    users = mongo.db.movies.find()
    movies_list = [{'name': user['name'], 'movie': user['movie'], 'actor': user['actor']} for user in users]
    return jsonify(movies_list)


@app.route('/getOneMovie/<id>', methods=['GET'])
def get_one_movie(id):
    user = mongo.db.movies.find_one({'_id': ObjectId(id)})
    if user:
        return jsonify(user)
    return jsonify({'error': 'ID not found'}), 404


@app.route('/deleteMovie/<id>', methods=['GET', 'POST'])
def delete_movie(id):
    result = mongo.db.movies.delete_one({'_id': ObjectId(id)})
    if result.deleted_count > 0:
        return jsonify({'message': 'User deleted successfully'})
    return jsonify({'error': 'ID not found'}), 404


@app.route('/updateMovie/<id>', methods=['POST'])
def update_movie(id):
    request_data = request.get_json()
    request_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result = mongo.db.movies.update_one({'_id': ObjectId(id)}, {'$set': request_data})
    if result.modified_count > 0:
        return jsonify({'message': 'User updated successfully'})
    return jsonify({'error': 'User not found or no changes applied'}), 404


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
    server.run(app, host='0.0.0.0', port=5000, debug=True)
