from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit
import random


app = Flask(__name__)
socketio = SocketIO(app)

rooms = {}
@app.route('/')
def home():
    return render_template('index.html', rooms=rooms)


@app.route("/available-rooms")
def available_rooms():
    return render_template("available-rooms.html", rooms = rooms)

# @app.route('/room/<room_id>')
# def room(room_id):
#     print('triggered')
#     return render_template('room.html', room_id=room_id, story=rooms[room_id]['story'])

@app.route('/room/<room_id>', methods=['POST'])
def submit_username(room_id):
    username = request.form.get('username') 

    if room_id not in rooms:
        return jsonify(error="Room not found"), 404
    return render_template('room.html', username=username, room_id=room_id, story=rooms[room_id]['story'])

@app.route('/create-room')
def create_room():
    room_id = str(random.randint(100, 999))
    rooms[room_id] = {'story':[]}
    return render_template('room-linker.html', room_id=room_id)


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
    join_room(room_id)
    print(f"user has joined room {room_id}")


if __name__=="__main__":
    socketio.run(app, debug =True)