from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, join_room, leave_room, emit
import random


app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = "secret"


rooms = {}
@app.route('/')
def home():
    return render_template('index.html', rooms=rooms)



@app.route('/set-username', methods=['POST'])
def set_username():
    print('username')

    username = request.form.get('username')
    session['username'] = username

    if not username:
        return "Username is required!", 400
    return render_template("main-content.html", username=username, rooms=rooms)

@app.route('/room/<username>/<room_id>')
def room(username, room_id):
    if room_id not in rooms:
        return "Room not found", 404

    return render_template('room.html', username=username, room_id=room_id, story=rooms[room_id]['story'])


@app.route('/room/<room_id>', methods=['POST'])
def submit_username(room_id):
    username = request.form.get('username') 

    if room_id not in rooms:
        return jsonify(error="Room not found"), 404
    return render_template('room.html', username=username, room_id=room_id, story=rooms[room_id]['story'])

@app.route('/create-room', methods=['POST'])
def create_room():
    room_id = str(random.randint(100, 999))
    rooms[room_id] = {'story':[], 'users':[]}
    return render_template('room-linker.html', room_id=room_id, username =session['username'] )


@app.route('/<room_id>/submit_line', methods=['POST'])
def submit_line(room_id):
    line = request.form.get('line')
  
    print(line, room_id, rooms)
    if room_id not in rooms:
        return jsonify(error="Room not found"), 404
    
    rooms[room_id]['story'].append(line)
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


    print(f"{username} has joined room {room_id}")
    socketio.emit('update_users', {
        'users':rooms[room_id]['users']
    }, room=room_id)


if __name__=="__main__":
    socketio.run(app, debug =True)