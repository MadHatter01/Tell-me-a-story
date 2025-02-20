from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import random


app = Flask(__name__)
socketio = SocketIO(app)

rooms = {}
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/room/<room_id>')
def room(room_id):
    return render_template('room.html', room_id=room_id)


@app.route('/create-room')
def create_room():
    room_id = str(random.randint(100, 999))
    rooms[room_id] = {'story':[], 'current':0, 'turns':[]}
    print(rooms)
    return render_template('room-linker.html', room_id=room_id)


@app.route('/<room_id>/submit_line', methods=['POST'])
def submit_line(room_id):
    line = request.form.get('line')
  
    print(line, room_id, rooms)
    if room_id not in rooms:
        return jsonify(error="Room not found"), 404
    
    rooms[room_id]['story'].append(line)

    return render_template('story.html', story=rooms[room_id]['story'])

if __name__=="__main__":
    socketio.run(app, debug =True)