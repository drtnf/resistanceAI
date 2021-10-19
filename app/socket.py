from flask import Flask, render_template, session, copy_current_request_context
from flask_socketio import SocketIO, emit, connect, disconnect
from threading import Timer
from app.models import Student
from app import socketio

#app = Flask(__name__)
#socketio = SocketIO(app)
#socketio = socketio.Server()
callbacks = {}

@app.route('/')#basic landing page
def index():
    return render_template('index.html')


def send_to_student(name, data, student, callback=None, timeout=5):
    '''
    name is the name of the function being called
    data is a json data object
    student is the student id to whom the message is being sent
    callback is an optional parameter to be called when the student next send a message
    timeout is the number of seconds until the callback reverts to default.
    '''
    if callback is not None:
        callbacks.put(student, callback)
    emit(name, data, room=str(student))
    #some timing stuff
    Student.get(student).set_timer(5, callback)
    
@socketio.on('send_action')
def on_action(data):
    student = data['student']
    token = data['token']
    action = data['action']
    s = Student.get(student)
    ##hmmmm need game to get player id? almost better to have this tied to plays
    ##or include game in the call.
    
    #check token and get player id
    #get callback from callbacks dictionary
    if student in callbacks:
        student.cancel_timer()
        callbacks[student]('player_id'=player_id)
        callbacks.remove(student)




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
