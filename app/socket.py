from flask import Flask, render_template, session, copy_current_request_context
from flask_socketio import SocketIO, emit, connect, disconnect
from threading import Timer
from app.models import Student
from app import socketio

#app = Flask(__name__)
#socketio = SocketIO(app)
#socketio = socketio.Server()
'''
dictionary for handling responses to action_requests
'''
callbacks = {}

'''
game queue of players waiting to join game
'''
player_queue = []


@app.route('/')#basic landing page
def index():
    return render_template('index.html')


def send(name, data, student_id):
    '''
    name is the name of the function being called
    data is a json data object
    student is the student id to whom the message is being sent
    '''
    emit(name, data, room=str(student_id))


def request_action(action, data, student_id, callback, timeout=5):
    game_id = data['game_id']
    rnd = data['round']
    mission = data['mission']
    player_id = data['player_id']
    callbacks.put((student_id, game_id, rnd, mission, action), callback)
    emit(action, data, room=str(student_id))
    t = Timer(timeout, default_action, args=[student_id, game_id, rnd, mission, action])
    t.start()

def default_action(student_id, game_id, rnd, mission, action):
    return lambda:
        if (student_id, game_id, rnd, mission, action) in callbacks:
            callbacks[(student_id, game_id, rnd, mission, action)]()
            callbacks.remove((student_id, game_id, rnd, mission, action))
            emit('timeout', {'game_id': game_id, 'round': rnd, 'mission': mission, 'action': action}, room=str(student_id)) 

@socketio.on('send_action')
def on_action(data):
    student_id = data['student_id']
    game_id = data['game_id']
    rnd = data['round']
    mission = data['mission']
    action = data['action']
    player_id = data['player_id']
    token = data['token'] # use g.user, and include token-auth in url
    s = Student.get(student_id)
    game = Game.get(game_id)
    if token == s.token and game.get_student_id(player_id)== student_id: # else some thing funny going on.
        if (student_id, game_id, rnd, mission, action) in callbacks:
            callbacks[(student_id, game_id, rnd, mission, action)](data[choice])
            callbacks.remove((sudent_id, game_id, rnd, mission, action))
        #else method has timed out. do nothing
    else:
        pass #throw a shenenigans exception

#####
#need code here for handling connect events.
#####

'''
Process:
On connection request:
    check authentication
    add to queue
    acknowledge connection
Every X seconds check if queue longer than 5:
    If queue >=5:
       pick random game size, N, from 5 to min(10, queue_length)
       sample N players from first 20 people in queue, 
       put N players in array players
       create new Game.
       call g.start(players)

two functions to write
'''
@socketio.on('connect')
def connect():#add token auth flag???
    '''
    On connection request:
    check authentication
    add to queue
    acknowledge connection
    '''
    with app.app_context():
        student_id = g['user']
        join_room(str(student_id))
        if student_id not in player_queue:
            player_queue.append(student_id)
        send(student_id + ' has been added to game queue.', to=str(student_id))

def start_game():        
    '''
    Every X seconds check if queue longer than 5:
    If queue >=5:
       pick random game size, N, from 5 to min(10, queue_length)
       sample N players from first 20 people in queue, 
       put N players in array players
       create new Game.
       call game.start(players)
    '''
    pass










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
