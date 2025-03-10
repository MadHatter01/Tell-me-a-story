from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, join_room, leave_room, emit
import random
import uuid
import time
from faker import Faker

fake = Faker()




app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = "secret"


rooms = {}

def next_turn(room_id):
    if room_id not in rooms or len(rooms[room_id]['users']) == 0:
        return
    
    rooms[room_id]['currentTurn'] = (rooms[room_id]['currentTurn'] + 1)% len(rooms[room_id]['users'])
    socketio.emit('turn_update',{
        'active_user':rooms[room_id]['users'][rooms[room_id]['currentTurn']]
    }, room=room_id)

@app.route('/')
def home():
    return render_template('index.html', rooms=rooms, randomname = fake.name())



@app.route('/set-username', methods=['POST'])
def set_username():

    username = request.form.get('username')
    session['username'] = username
    session['id'] = str(uuid.uuid4())

    if not username:
        return "Username is required!", 400
    return render_template("main-content.html", username=username, rooms=rooms)

@app.route('/room/<genre>/<username>/<room_id>')
def room(username, room_id, genre):
    if room_id not in rooms:
        return "Room not found", 404

    return render_template('room.html', username=username, room_id=room_id, story=rooms[room_id]['story'], genre=genre)


@app.route('/room/<room_id>', methods=['POST'])
def submit_username(room_id):
    username = request.form.get('username') 

    if room_id not in rooms:
        return jsonify(error="Room not found"), 404
    return render_template('room.html', username=username, room_id=room_id, story=rooms[room_id]['story'])

@app.route('/create-room', methods=['POST'])
def create_room():
    room_id = str(random.randint(100, 999))
    rooms[room_id] = {'story':[], 'users':[], 'currentTurn':0}
    genres = ['comedy', 'drama', 'horror', 'romantic', 'medieval', 'tragedy']

    return render_template('room-linker.html', room_id=room_id, username =session['username'], genre=random.choice(genres) )


@app.route('/<username>/<room_id>/submit_line', methods=['POST'])
def submit_line(username, room_id):
    line = request.form.get('line')

    index = rooms[room_id]['currentTurn']
    current_user = rooms[room_id]['users'][index]
  

    
    print(line, room_id, rooms)
    if room_id not in rooms:
        return jsonify(error="Room not found"), 404
    print(line)
    rooms[room_id]['story'].append(f"{username}: {line}")
    next_turn(room_id)

    socketio.emit('update_story', {'story': rooms[room_id]['story']}, room=room_id)
    return render_template('story.html', story=rooms[room_id]['story'])

@socketio.on('connect')
def handle_connect():
    print('someone connected!')

@socketio.on('disconnect')
def handle_disconnect():
    print('someone disconnected')

@socketio.on('join')
def handle_join(data):
    room_id = data['room_id']
    username = data['username']
    if room_id not in rooms:
        return
    
    join_room(room_id)
    if username not in rooms[room_id]['users']:
        rooms[room_id]['users'].append(username)

    if len(rooms[room_id]['users'])==1:
        rooms[room_id]['currentTurn'] = 0


    print(f"{username} has joined room {room_id}")
    socketio.emit('update_users', {
        'users':rooms[room_id]['users'],
        'active_user':rooms[room_id]['users'][rooms[room_id]['currentTurn']]
    }, room=room_id)

    socketio.emit('turn_update', {
        'active_user': rooms[room_id]['users'][rooms[room_id]['currentTurn']]
    }, room=room_id)


if __name__=="__main__":
    socketio.run(app, debug =True)