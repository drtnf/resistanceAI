from flask import Flask, render_template, session, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect
from threading import Timer
from app import app, socketio
from functools import wraps

#from app.models import Student, Game

'''
dictionary for handling responses to action_requests
'''
callbacks = {}

'''
game queue of players waiting to join game
'''
player_queue = []


def token_required(f):
    '''
    Decorator for token authentication
    '''
    @wraps(f)
    def decorated(data):
        try:
            student = app.models.Student.check_token(id=data['token'])
            if student:
                return f(data)
            else:
                send('Invalid token', to=data['student_id'])
        except Exception as e:
                print(str(e))
    return decorated



@app.route('/')#basic landing page with scoreboard
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    pass

@app.route('/register')
def register():
    pass

def send(name, data, student_id):
    '''
    name is the name of the function being called
    data is a json data object
    student is the student id to whom the message is being sent
    names are ['new_game', 'game_outcome', 'round_outcome', 'mission_outcome', 'vote_outcome']
    '''
    with app.app_context():
        emit(name, data, namespace = "/", room=str(student_id))


def request_action(action, data, student_id, callback, timeout=5):
    '''
    action is the name of the method being called,
    data is the parameters of the method, nad the context of the request,
    student_id in the id of the agent recieving the request
    callback is the method to be executed when the response is received, 
    timeout is how long the socket will wait for a response.
    actions are ['propose_mission', 'vote', 'betray']
    '''
    game_id = data['game_id']
    rnd = data['round']
    mission = data['mission']
    player_id = data['player_id']
    callbacks.put((student_id, game_id, rnd, mission, action), callback)

    with app.app_context():
        emit(action, data, namespace = "/", room=str(student_id))

    t = Timer(timeout, default_action, args=[student_id, game_id, rnd, mission, action])
    t.start()

def default_action(student_id, game_id, rnd, mission, action):
    if (student_id, game_id, rnd, mission, action) in callbacks:
        callbacks[(student_id, game_id, rnd, mission, action)]()
        callbacks.remove((student_id, game_id, rnd, mission, action))

        with app.app_context():
            emit('timeout', {'game_id': game_id, 'round': rnd, 'mission': mission, 'action': action}, namespace = "/", room=str(student_id)) 
    

@socketio.on('send_action')
@token_required
def on_action(data):
    student_id = data['student_id']
    game_id = data['game_id']
    rnd = data['round']
    mission = data['mission']
    action = data['action']
    player_id = data['player_id']
    if (student_id, game_id, rnd, mission, action) in callbacks:
        callbacks[(student_id, game_id, rnd, mission, action)](data['player_id'], data['choice'])
        callbacks.remove((sudent_id, game_id, rnd, mission, action))

#####
#need code here for handling connect events.
#####

@socketio.on('connect')
def connect():
    '''
    On connection request:
    check authentication
    add to queue
    acknowledge connection
    '''
    with app.app_context():#check token here?
        student_id = g['user']#check if this is best way???
        token = g['token']
        if Student.check_token(token).id == student_id:
            join_room(str(student_id))
            if student_id not in player_queue:
                player_queue.append(student_id)
                send(student_id + ' has been added to game queue.', namespace = "/", to=str(student_id))
                t = threading.timer(5, start_game)
                t.start()
            else:
                send(student_id + ' already in game queue.', namespace = "/", to=str(student_id))
        else:  
            send('Invalid token', namespace = "/", to=str(student_id))


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
    num_waiting = len(player_queue)
    if num_waiting>=5:
        g = app.models.Game() 
        player_num = random.randrange(5, min(10, num_waiting))
        agents = player_queue[:player_num]#just grab front agents...?
        player_queue = player_queue[player_num:]
        g.start(agents)
    #else do nothing.


# Just leave this at the bottom, probably not necessary to have a button but good for testing 
@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()


if __name__ == '__main__':
    socketio.run(app, debug = True)
