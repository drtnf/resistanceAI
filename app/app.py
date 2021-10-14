from flask import Flask, render_template, session, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

# Cool, so here's boilerplate for any events we do 
# We need to do three, but this is just a placeholder for any event
@socketio.on('event', namespace='/test')
def test_message(message):
    
    # This just keeps track of which sequential message number this is for the session
    session['receive_count'] = session.get('receive_count', 0) + 1

    # Send back the data and the count
    emit('response',
         {'data': message['data'], 'count': session['receive_count']})

# Just leave this at the bottom, probably not necessary to have a button but good for testing 
@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    # Just kept the same message template, don't really need a count but I copied it from above 
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('response',
         {'data': 'disconnected.', 'count': session['receive_count']},
         callback = can_disconnect)

if __name__ == '__main__':
    socketio.run(app, debug = True)