from agent import Agent
from app import socketio
from flask_socketio import send, emit
from threading import Timer
import json
import random

#need external code that records the student number to Game map, to appropriate socket agent..
#or can we write client harnesses that just use http requests to poll for data and post?

class SocketAgent: #not subclassing from agent!        
    '''A sample implementation of a random agent in the game The Resistance'''
    #need to record a name for the agent, and a room id
    #each agent is in a separate room.
    def __init__(self, name, student_number, room):
        '''
        Initialises the agent.
        Nothing to do here.
        '''
        self.name = name
        self.student_number = student_number
        self.room = room
        self.timer = None
        self.current_req = None


    def new_game(self, number_of_players, player_number, spy_list, game):
        '''
        initialises the game, informing the agent of the 
        number_of_players, the player_number (an id number for the agent in the game),
        and a list of agent indexes which are the spies, if the agent is a spy, or empty otherwise
        '''
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.is_spy = player_number in spy_list
        #just transfers data
        data = {
                'number_of_players':number_of_players,
                'player_number': player_number,
                'spy_list': spy_list
                }
        emit('new_game', json.dump(data), room=self.room)
        self.game = game

    def is_spy(self):
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list

###include utility timeout function?
###sets a timer 
    def time_out(self):
        if self.current_req is not None:
            action = self.current_req['action']
            rnd = self.current_req['round']
            mission = self.current_req['mission']
            emit('time_out', json.dump(self.current_req), room=self.room)
            if action is 'propose_mission':
                team = []
                while len(team)<team_size:
                    agent = random.randrange(team_size)
                    if agent not in team:
                        team.append(agent)
                self.game.mission(self.player_number, rnd, mission, team)
            elif action is 'vote':    
                self.game.vote(self.player_number, rnd, mission, False)
            elif action is 'betray':    
                self.game.betray(self.player_number, rnd, mission, False)
            self.current_req = None    



    def req_mission(self, team_size, betrayals_required = 1, rnd, mission):
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned. 
        betrayals_required are the number of betrayals required for the mission to fail.
        '''
        data = {
                'team_size': team_size,
                'betrayals_required': betrayals_required,
                'round': rnd,
                'mission': mission
                }
        emit('propose_mission', json.dump(data), room=self.room)
        self.current_action = {'action':'propose_misson', 'round':rnd, 'mission':mission}
        t = Timer(5.0, self.time_out) 
        #after 5 seconds call rec_mission with an empty team 
        #should probably log the time out????add this is later
        #need a timeout function
        t.start()

    @socketio.on('propose_mission', room=self.room)
    def rec_mission(self, data):
        team = data['team']
        rnd = data['round']
        mission = data['mission']
        if self.current_action['action'] == 'propose_mission' and \
                self.current_action['round'] == rnd and \
                self.current_action['mission'] == mission:
            self.current_action = None
        if not check_team(team, Agent.mission_sizes[self.number_of_players][rnd]):
            team = []
            while len(team)<team_size:
                agent = random.randrange(team_size)
                if agent not in team:
                     team.append(agent)
        self.game.mission(self.player_number, rnd, mission, team)        

    '''
    checks a valid team is returned,
    containing the right number of members,
    where every member is an int from 0 to numplayers-1
    and no member is repeated
    '''
    def check_team(self, team, team_size):
        chk = len(team)==team_size
        for i in range(team_size):
            chk = chk and 0<=int(team[i]) and int(team[i]) <= self.number_of_players and not team[i] in team[i+1:]
        return chk    
            

    def req_vote(self, team, leader, rnd, mission):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        leader is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        data = {
                'team': team,
                'leader': proposer, 
                'round': rnd,
                'mission': mission
                }
        emit('vote', json.dump(data), room=self.room)
        self.current_action = {'action':'vote', 'round':rnd, 'mission':mission}
        t = Timer(5.0, self.time_out) 
        #after 5 seconds submot a default no vote. 
        t.start()
        
    @socketio.on('vote', room=self.room)
    def rec_vote(self, data):
        vote = data['vote']
        rnd = data['round']
        mission = data['mission']
        if self.current_action['action'] == 'vote' and \
                self.current_action['round'] == rnd and \
                self.current_action['mission'] == mission:
            self.current_action = None
        self.game.vote(self.player_number, rnd, mission, vote)        

    #just informative action
    def vote_outcome(self, mission, proposer, votes):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
        data = {
                'mission': mission,
                'proposer': proposer,
                'votes': votes
                }
        emit('vote_outcome', json.dump(data), room = self.room)


    def req_betray(self, team, proposer, rnd, mission):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        '''
        data = {
                'team': team,
                'leader': proposer, 
                'round': rnd,
                'mission': mission
                }
        emit('betray', json.dump(data), room=self.room)
        self.current_action = {'action':'betray', 'round':rnd, 'mission':mission}
        t = Timer(5.0, self.time_out) 
        #after 5 seconds submit a default no betray. 
        t.start()

    @socketio.on('vote', room=self.room)
    def rec_betray(self, data):
        betray = data['betray']
        rnd = data['round']
        mission = data['mission']
        if self.current_action['action'] == 'betray' and \
                self.current_action['round'] == rnd and \
                self.current_action['mission'] == mission:
            self.current_action = None
        self.game.betray(self.player_number, rnd, mission, betray)        


    #just informative
    def mission_outcome(self, mission, proposer, betrayals, mission_success):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        betrayals is the number of people on the mission who betrayed the mission, 
        and mission_success is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It iss not expected or required for this function to return anything.
        '''
        data = {
                'mission': mission,
                'proposer': proposer,
                'betrayals': betrayals,
                'mission_success': mission_success
                }
        emit('mission_outcome', json.dump(data), room=self.room)

    #just informative
    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''
        data = {
                'rounds_complete': rounds_compete,
                'mission_failed': mission_failed
                }
        emit('round_outcome', json.dump(data), room=self.room)

    #just informative
    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        data = {
                'spies_win': spies_win,
                'spies': spies
                }
        emit('game_outcome', json.dump(data), room=self.room)
        



