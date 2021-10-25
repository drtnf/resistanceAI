import base64
from app import db, login, socket
from flask_socketio import send, emit
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import url_for
from datetime import datetime, timedelta
import os
import json
#
#nice idea to abstract out socket with io (input?) for debugging purposes?
#Only 7 instances to cover?
#
#resistance imports: probably just hack the code in here?
from app.agent import Agent
import random

#toggle to false for command line debugging
socket_on = False

#allows login to get student from database, given id
#will be stored as current_user?
@login.user_loader
def load_student(id):
  return Student.query.get(int(id))

class Student(UserMixin, db.Model):
    '''
    Student class to represent a classmember who submits an agent to the tournament.
    '''
    __tablename__='student'
    id = db.Column(db.String(8), primary_key = True)#prepopulate
    first_name = db.Column(db.String(64))#prepopulate
    last_name = db.Column(db.String(64))#prepopulate
    agent_name = db.Column(db.String(64))#submitted by student
    agent_source = db.Column(db.LargeBinary())
    password_hash = db.Column(db.String(128))#arbitrary password
    #token authetication for api
    token = db.Column(db.String(32), index=True, unique = True)
    token_expiration=db.Column(db.DateTime)
    #non-database fields
    games = db.relationship('Game', secondary='plays') 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    ###Token support methods for api

    def get_token(self, expires_in=3600000):#1000 hours per token. Not limitted to browser.
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now+timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        student = Student.query.filter_by(token=token).first()
        if student is None or student.token_expiration < datetime.utcnow():
            return None
        return student

    def start_timer(self, time, callback, args=[]):
        '''
        Each student has a timer for measuring timeouts
        '''
        self.timer = Timer(time, callback, args)
        self.timer.start()

    def stop_timer(self):
        '''
        When a client returns in time
        '''
        self.timer.cancel()

    '''Adding in dictionary methods to convert to JSON
       Format
       {
       'id':'19617810',
       'first_name':'Timothy',
       'last_name': 'French',
       'agent_name': 'Agent Tim',
       'agent_source': 'return None'
      }'''

    def to_dict(self):
      data = {
          'id': self.id,
          'first_name':self.first_name,
          'last_name': self.last_name,
          'agent_name': self.agent_name,
          'agent_source': self.agent_source
      }
      return data

    def from_dict(self, data):
      for attr in ['agent_name', 'agent_source', 'pin']:
          if attr in data:
              setattr(self, attr, data[attr])

    def __repr__(self):
        return '[Number:{}, Name:{}]'.format(
                self.id, \
                self.__str__()
                )

    def __str__(self):
      return self.first_name+' '+self.last_name +' ('+self.agent_name+')'


####
#repr, str, to_dict, from_dict for all models below
####

class Plays(db.Model):
    '''
    A class for recording a student's agent's role in a game.
    '''
    __tablename__ = 'plays'
    game_id = db.Column(db.Integer, db.ForeignKey('game.game_id'),primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key = True)
    agent_number = db.Column(db.Integer) #0-9, their identifier in the game
    time = db.Column(db.DateTime)
    #references
    student = db.relationship('Student', backref=db.backref('plays', lazy='dynamic'))
    game = db.relationship('Game', backref=db.backref('plays', lazy='dynamic'))

    def to_dict(self):
        return {'game_id': self.game_id,
                'student_id': self.student_id,
                'agent_number': self.agent_number,
                'time': self.time
                }

    def from_dict(self, data):
        for attr in ['game_id', 'student_id', 'agent_number', 'time']:
            if attr in data:
               setattr(self, attr, data[attr])

    def __str__(self):
        return 'Student ' + str(self.student_id) + \
                ' was player ' + str(self.agent_number) + \
                ' in game ' + str(self.game_number) + \
                ' on ' + str(self.time)

    def __repr__(self):
        return json.dumps(self.to_dict(), default=str) # DateTime is not serializable


#########
#Game model for executing a single game
#########

class Game(db.Model):
    '''
    A class for recording a full play of a game of The Resistance.
    '''
    #SQLAlchemy vars
    __tablename__='game'
    game_id = db.Column(db.Integer, primary_key = True)
    score = db.Column(db.Integer)
    num_players = db.Column(db.Integer)
    spies = db.Column(db.String(5)) #only populated at the end.
    #backrefs for rounds and missions
    rounds = db.relationship('Round', backref='game',lazy=False)
    students = db.relationship('Student', secondary='plays')

    def start(self, students):
        '''
        Given array of students, check unique, shuffle, and instantiate plays relation
        Then allocate spies, and broadcast to students
        Then commence first round
        '''
        if len(students)<5 or len(students)>10:
            raise Exception('Student array out of range')
        for i in range(len(students)):
            if students[i] in students[i+1:]: raise Exception('Students duplicated')
        #shuffle student array
        random.shuffle(students)
        time = datetime.utcnow()
        self.num_players = len(students)
        for i in range(self.num_players):
            plays = Plays()
            plays.agent_number = i
            plays.game = self
            plays.student = students[i]
            plays.time = time
            db.session.add(plays)
        #allocate spies
        self.spies = ''
        while len(self.spies) < Agent.spy_count[self.num_players]:
            spy = str(random.randrange(self.num_players))
            if spy not in self.spies:
                self.spies = self.spies+str(spy)
        #start game for each agent        
        for agent_id in range(self.num_players):
            spy_list = [spy for spy in self.spies if str(agent_id) in self.spies]
            #self.spies_list = [spy for spy in self.spies]
            data = {
                    'game_id': self.game_id,
                    'number_of_players': self.num_players,
                    'player_number': agent_id,
                    'spy_list': spy_list
                    }
            if socket_on: socket.send('new_game', data, self.get_student_id(student))
            else: print('new_game', data, self.get_student_id(agent_id))
        #initialise rounds and state variables
        self.rounds = []
        #commence rounds
        leader = 0
        db.session.commit()
        self.next_round(leader)

    def get_student_id(self, player_id):
        '''
        maps a players id to the corresponding student_id
        '''
        return [p.student_id for p in self.plays if p.agent_number == player_id][0]

#not required?
#    def student_to_index(self, student):
#        return [p.agent_number for p in self.plays if p.student == student][0]

    def next_round(self, leader):
        '''
        moves to the next round, or finialises the game  if five rounds have been played
        '''
        if len(self.rounds) == 5: #game over
            self.spies_win = len([r for r in self.rounds if r.is_successful()]) < 3
            data = {
                    'game_id': self.game_id,
                    'spies_win': self.spies_win,
                    'spies': self.spies
                    }
            for agent_id in range(self.num_players):
                if socket_on: socket.send('game_outcome', data, self.get_student_id(agent_id))
                else: print('game_outcome', data, self.get_student_id(agent_id))
            db.session.add(self)# persistance, fill in
            db.session.commit()
        else:
            rnd = Round(game_id=self.game_id, round_num=len(self.rounds))
            db.session.add(rnd)
            self.rounds.append(rnd)
            self.rounds[-1].next_mission(leader)


    def to_dict(self):
        return {'game_id': self.game_id,
                'score': self.score,
                'num_players': self.num_players,
                'spies': self.spies,
                'rounds': [r.to_dict() for r in self.rounds]
                }

    def from_dict(self, data):
        for attr in ['game_id', 'score', 'num_players', 'spies']:
            if attr in data:
               setattr(self, attr, data[attr])
        if 'rounds' in data:
            self.rounds = [r.from_dict(d) for d in data['rounds']]

    def __str__(self):
        desc = 'Game: ' + str(self.game_id) + \
                '\nScore: ' + str(self.score) + \
                '\nNumber of Players: ' + str(self.num_players) + \
                '\nSpies: ' + str(self.spies) + \
                '\nRounds: '
        rnd = 1
        for r in self.rounds:
            desc =  desc + '\n' + str(rnd) +  str(r)
            n = n+1
        return desc

    def __repr__(self):
        return json.dumps(self.to_dict())

########################################
#Round Class
#######################################

class Round(db.Model):
    '''
    A class for representing a full play of a round in a game of The Resistance.
    '''
    __tablename__ = 'round'
    round_id = db.Column(db.Integer, primary_key = True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.game_id'), nullable = False)
    success = db.Column(db.Boolean)#resistance wins
    round_num = db.Column(db.Integer)
    missions = db.relationship('Mission',backref='round',lazy=False)

    '''
    run the next mission
    '''
    def next_mission(self, leader):
        if self.missions is None:
            self.missions = []
        mission = Mission(round_id = self.round_id, leader=leader, mission_num=len(self.missions))
        db.session.add(mission)
        self.missions.append(mission)
        self.missions[-1].req_team()

    def outcome(self):
        self.success = self.is_successful()
        data = {
                'game_id': self.game_id,
                'round_num': self.round_num,
                'missions_failed': len([r for r in self.game.rounds if not r.is_successful()])
                }
        for student in self.game.students:
            if socket_on: socket.send('round_outcome', data, student)
            else: print('round_outcome', data, student)
        self.game.next_round((self.missions[-1].leader+1)%self.game.num_players)

    def is_successful(self):
        '''
        returns true is the mission was successful
        '''
        return len(self.missions)>0 and self.missions[-1].approved and self.missions[-1].success

    def to_dict(self):
        return {'round_id': self.round_id,
                'game_id': self.game_id,
                'success': self.success,
                'round_num': self.round_num,
                'missions': [m.to_dict() for m in self.missions]
                }

    def from_dict(self, data):
        for attr in ['round_id', 'game_id', 'success', 'round_num']:
            if attr in data:
               setattr(self, attr, data[attr])
        if 'missions' in data:
            self.missions = [m.from_dict[mission] for mission in data['missions']]

    def __str__(self):
        desc = '\nRound id: ' + self.round_id + \
                '\n Round ' + self.round_num + ' of game ' + self.game_id + \
                '\n Resistance wins!' if self.success else '\n Spies win!' + \
                '\n Missions: '
        for m in self.missions:
            desc = desc + str(m)
        return desc


    def __repr__(self):
        return json.dumps(self.to_dict())


################
#Mission Class
################

class Mission(db.Model):
    '''
    A class for representing each mission, the team, the leader,
    the vote and whether it was a success.
    '''
    __tablename__ = 'mission'
    mission_id = db.Column(db.Integer, primary_key = True)
    round_id = db.Column(db.Integer, db.ForeignKey('round.round_id'), nullable = False)
    mission_num = db.Column(db.Integer)
    leader = db.Column(db.Integer)
    team_string = db.Column(db.String(5))
    vote_string = db.Column(db.String(10))
    approved = db.Column(db.Boolean)
    fails = db.Column(db.String(4))
    success = db.Column(db.Boolean)


    def req_team(self):
        '''
        socket emit propose team to room leader_id.student number, 
        with token expected for mission x in round y
        '''
        self.num_players = self.round.game.num_players
        rnd = self.round.round_num
        self.team_size = Agent.mission_sizes[self.num_players][rnd]
        self.fails_required = Agent.fails_required[self.num_players][rnd]
        student_id = self.round.game.get_student_id(self.leader)
        player_id  = self.leader
        data = {
                'game_id': self.round.game.game_id,
                'round': self.round.round_num,
                'mission': self.mission_num,
                'player_id': player_id,
                'team_size': self.team_size,
                'betrayals_required': self.fails_required
                }
        if socket_on: 
            socket.request_action('propose_mission', data, student_id, lambda x: self.rec_team(player_id, x))
        else:
            self.rec_team(player_id, input('propose_mission'+'\n'+str(data)+'\n'+str(student_id)+'\n> '))


    def rec_team(self, leader_id, team_string=''):
        '''
        receive team proposed by leader
        '''
        self.team_string = self.check_team(team_string)
        if not self.team_string: # if check_team returned False, generate a random team
            self.team_string = self.random_team()
        self.vote_string = ''
        if self.mission_num<4:
            self.req_vote()
        else:
            self.approved = True
            self.req_betray()


    def check_team(self, team):
        '''
        checks a valid team is returned,
        containing the right number of members,
        where every member is an int from 0 to numplayers-1
        and no member is repeated
        '''
        try:
            # remove duplicates, convert to ints, then sort
            team = sorted([int(i) for i in set(team)])
        except ValueError:
            # converting to int did not work, so there were some non-digit chars in team string
            return False
        if len(team) != self.team_size:
            return False
        # assuming that team is already in sorted order
        if 0 <= team[0] and team[-1] < self.num_players:
            # convert back to string
            return "".join([str(i) for i in team])
        return False

    def random_team(self):
        '''
        Generates a random team string
        for num_players with given team_size
        '''
        team = []
        while len(team)<self.team_size:
            agent = random.randrange(self.num_players)
            if agent not in team:
                team.append(agent)
        return "".join([str(i) for i in sorted(team)])

    def req_vote(self):
        '''
        send a request to each player for a vote on the mission propsoed by the leader,
        and then wait for responses.
        '''
        self.votes_required = list(range(self.num_players))
        for player_id in range(self.num_players):
            student_id = self.round.game.get_student_id(player_id)
            #need map of students to agents?
            data = {
                    'game_id': self.round.game.game_id,
                    'round': self.round.round_num,
                    'mission': self.mission_num,
                    'player_id': player_id,
                    'team': self.team_string,
                    'leader': self.leader
                }
            if socket_on:
                socket.request_action('vote', data, student_id, lambda x: self.rec_vote(player_id, x))
            else:
                self.rec_vote(player_id, input('vote'+'\n'+str(data)+'\n'+str(student_id)+'\n> '))

    def rec_vote(self, player, vote=False):
        '''
        Code called when votes are received, one by one
        '''
        if player in self.votes_required:
            self.vote_string = self.vote_string + (str(player) if vote else '')
            self.votes_required.remove(player)
        if not self.votes_required: #all votes recieved
            self.approved = len(self.vote_string)>self.num_players/2
            data = {
                    'game_id': self.round.game.game_id,
                    'round': self.round.round_num,
                    'mission': self.mission_num,
                    'team': self.team_string,
                    'leader': self.leader,
                    'votes_for': self.vote_string,
                    'approved': self.approved
                    }
            for player_id in range(self.num_players):
                student_id = self.round.game.get_student_id(player_id)
                if socket_on: socket.send('vote_outcome',data, student_id)
                else: print('vote_outcome',data, student_id)
            if(self.approved):
                self.req_betray()
            else:
                self.round.next_mission((self.leader+1)%self.num_players)

    def req_betray(self):
        '''
        Requests betrayal choice from teams spies
        '''
        #fix from Lauren, rename to make variables meaningful...
        self.team_spies = [int(i) for i in self.team_string if i in self.round.game.spies]
        self.fails = 0
        if not self.team_spies:
            self.success = True
            for player_id in range(self.num_players):
                student_id = self.round.game.get_student_id(player_id)
                data = {
                        'game_id': self.round.game.game_id,
                        'round': self.round.round_num,
                        'mission': self.mission_num,
                        'proposer': self.leader,
                        'betrayals': self.fails,
                        'mission_success': self.success
                        }
                if socket_on: socket.send('mission_outcome',data, student_id)
                else: print('mission_outcome',data, student_id)
            self.round.outcome()
        else:
            #build student spy list
            spies_list = self.team_spies.copy()
            for player_id in spies_list:
                student_id = self.round.game.get_student_id(player_id)
                data = {
                        'game_id': self.round.game.game_id,
                        'round': self.round.round_num,
                        'mission': self.mission_num,
                        'team': self.team_string,
                        'leader': self.leader
                       }
                if socket_on:
                    socket.request_action('betray', data, student_id, lambda x: self.rec_betray(player_id, x))
                else:
                    self.rec_betray(player_id, input('betray'+'\n'+str(data)+'\n'+str(student_id)+'\n> '))

    def rec_betray(self, player, betray=False):
        '''
        call back used when client returns with betrayal choice
        '''
        if player in self.team_spies:
            self.team_spies.remove(player)
            if betray: self.fails = self.fails+1
        if not self.team_spies: #all betrayals received
            self.success = self.fails < self.fails_required
            #emit mission outcome to all players
            for player_id in range(self.num_players):
                student_id = self.round.game.get_student_id(player_id)
                data = {
                        'game_id': self.round.game.game_id,
                        'round': self.round.round_num,
                        'mission': self.mission_num,
                        'proposer': self.leader,
                        'betrayals': self.fails,
                        'mission_success': self.success
                        }
                if socket_on: socket.send('mission_outcome',data, student_id)
                else:print('mission_outcome', data, student_id)
            self.round.outcome() 


    '''
    creates a dictionary in json format:
    {
    mission_id: 123,
    round_id: 456,
    leader: 0-9,
    team_string: '012',
    vote_string: '0123456',
    approved: true,
    fails: '02',
    success: false
    }
    '''
    def to_dict(self):
        return {
                'mission_id': self.mission_id,#hyperlink here?
                'round_id': self.round_id,
                'leader': self.leader,
                'team_string': self.team_string,
                'vote_string': self.vote_string,
                'approve': self.approved,
                'fails': self.fails,
                'success': self.success
                }

    def from_dict(self, data):
        for attr in ['mission_id', 'round_id', 'leader', 'team_string', 'vote_string', 'approve', 'fails', 'success']:
            if attr in data:
               setattr(self, attr, data[attr])

    def __str__(self):
        return 'Mission: '+self.mission_id + \
                ' in round: ' +self.round_id + \
                '\nLeader ' + self.leader + \
                'proposed team ' +self.team_string + \
                '\nThe votes for were ' + self.vote_string + \
                'and the mission was ' + \
                    ('not approved' if not self.approved else \
                    'approved\nThere were ' + len(self.fails) + 'failures and the mission ' + \
                    ('succeeded' if self.success else 'failed')
                    )


    def __repr__(self):
        return json.dumps(self.to_dict())

