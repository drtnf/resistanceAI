import asyncio
import sys
import socketio
import time
from random_agent import RandomAgent as Agent

sio = socketio.Client(logger=True, engineio_logger=True)

student_number = "19617810"
token = "O/c1PP0kemgx/oUvUVVtq1djvBWlJuLv"
url = 'http://localhost:5000'

agent = Agent('itsme')


@sio.event
def connect(data):
    print('Connected.')

@sio.event
def new_game(data):
    agent.new_game(data['number_of_players'], data['player_number'], [spy for spy in data['spy_list']])
    

@sio.event
def game_outcome(data):
    agent.game_outcome(data['spies_win'],[spy for spy in data['spies']])
    

@sio.event
def round_outcome(data):
    agent.round_outcome(data['round_num'], data['missions_failed'])
    

@sio.event
def mission_outcome(data):
    agent.mission_outcome(data['mission'], data['proposer'], data['betrayals'], data['mission_success'])

@sio.event
def vote_outcome(data):
    agent.vote_outcome(data['team'], data['leader'], [player for player in data['votes_for']])

@sio.event
def propose_mission(data):
    team = agent.propose_mission(data['team_size'], data['betrayals_required'])
    team_string = ('').join([str(c) for c in team])
    resp={
            'student_id': student_id,
            'token': token,
            'game_id': data['game_id'],
            'round': data['round'],
            'mission': data['mission'],
            'action': 'propose_mission',
            'player_id': data['player_id'],
            'choice': team_string
            }
    sio.emit('send_action', resp)
    

@sio.event
def vote(data):
    approve = agent.vote([player for player in data['team']], data['leader'])
    resp={
            'student_id': student_id,
            'token': token,
            'game_id': data['game_id'],
            'round': data['round'],
            'mission': data['mission'],
            'action': 'vote',
            'player_id': data['player_id'],
            'choice': approve
            }
    sio.emit('send_action', resp)
    
@sio.event
def betray(data):
    fail = agent.vote([player for player in data['team']], data['leader'])
    resp={
            'student_id': student_id,
            'token': token,
            'game_id': data['game_id'],
            'round': data['round'],
            'mission': data['mission'],
            'action': 'betray',
            'player_id': data['player_id'],
            'choice': fail
            }
    sio.emit('send_action', resp)


@sio.on('test_send')
def test_send():
    print("test send")


@sio.event
def disconnect():
    print('disconnected')


def main():
    sio.connect(url, transports='polling', auth={'token':token})
    # sio.connect('http://localhost:5000',
    #             headers={'X-Username': student_number, 'token':security_token})
    sio.wait()


if __name__ == '__main__':
    main()
    #main(sys.argv[1] if len(sys.argv) > 1 else None)
