from flask import Flask, render_template, session, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room
from threading import Timer
from app import app, socketio
from functools import wraps
import random

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
        from app.models import Student
        try:
            student = Student.check_token(data['token'])
            if student:
                return f(data)
            else:
                send('Invalid token', to=data['student_id'])
        except Exception as e:
                print(str(e))
    return decorated



@app.route('/')#basic landing page with scoreboard
def index():
    return app.send_static_file('index.html')


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
    print('DATA SENT', data, 'STUDENT:', student_id)
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
    global callbacks
    print('ACTION REQUESTED', data, 'ACTION:', action, 'STUDENT:', student_id)
    game_id = data['game_id']
    rnd = data['round']
    mission = data['mission']
    player_id = data['player_id']
    callbacks[(student_id, game_id, rnd, mission, action)] = callback
    with app.app_context():
        emit(action, data, namespace = "/", room=str(student_id))
    t = Timer(timeout, default_action, args=[student_id, game_id, rnd, mission, action])
    t.start()

def default_action(student_id, game_id, rnd, mission, action):
    global callbacks
    if (student_id, game_id, rnd, mission, action) in callbacks:
        #print('TIMEOUT')
        callbacks[(student_id, game_id, rnd, mission, action)](False)
        callbacks.pop((student_id, game_id, rnd, mission, action))

        with app.app_context():
            emit('timeout', {'game_id': game_id, 'round': rnd, 'mission': mission, 'action': action}, namespace = "/", room=str(student_id)) 
    

@socketio.on('send_action')
@token_required
def on_action(data):
    global callbacks
    print('ACTION RECIEVED', data)
    student_id = data['student_id']
    game_id = data['game_id']
    rnd = data['round']
    mission = data['mission']
    action = data['action']
    player_id = data['player_id']
    if (student_id, game_id, rnd, mission, action) in callbacks:
        f = callbacks.pop((student_id, game_id, rnd, mission, action))
        f(player_id, data['choice'])


@socketio.on('connect')
def connect(auth):
    '''
    On connection request:
    check authentication
    add to queue
    acknowledge connection
    '''
    global player_queue
    from app.models import Student
    with app.app_context():#check token here?
        token = auth['token']
        print(token)
        student=Student.check_token(token)
        join_room(str(student.id))
        if student:
            join_player_queue(student)
        else:  
            send('connect_attempt', {'msg': 'Invalid token'}, student.id)

def join_player_queue(student):
    print(student.id)
    if student.id not in player_queue:
        player_queue.append(student.id)
        send('connect_attempt', {'msg': str(student.id) + ' has been added to game queue.'}, student.id)
        t = Timer(5, start_game)
        t.start()
    else:
        send('connect_attempt', {'msg': str(student.id) + ' already in game queue.'}, student.id)


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
    from app.models import Game
    global player_queue
    num_waiting = len(player_queue)
    if num_waiting>=5:
        g = Game() 
        print('NEW GAME:', g.game_id) 
        player_num = random.randrange(5, min(11, num_waiting+1))
        agents = []
        for i in range(player_num): agents.append(player_queue.pop(0))
        #agents = player_queue[:player_num]#just grab front agents...?
        #player_queue = player_queue[player_num:]
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
