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
    return render_template('room-linker.html', room_id=room_id)


@app.route('/submit_line', methods=['POST'])
def submit_line():
    line = request.form.get('line')
    print(line)
    return f"<p>{line}</p>"

if __name__=="__main__":
    socketio.run(app, debug =True)