import base64
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import url_for
from datetime import datetime, timedelta
import os
import json

#resistance imports: probably just hack the code in here?
from agent import Agent
from random_agent import RandomAgent
import random




#allows login to get student from database, given id
#will be stored as current_user?
@login.user_loader
def load_student(id):
  return Student.query.get(int(id))

class Student(UserMixin, db.Model):
  '''
  Student class to represent a classmember who submits an agent to the tournament.
  '''
  __tablename__='students'
  id = db.Column(db.String(8), primary_key = True)#prepopulate
  first_name = db.Column(db.String(64))#prepopulate
  last_name = db.Column(db.String(64))#prepopulate
  agent_name = db.Column(db.String(64))#submitted by student
  agent_src = db.Column(db.LargeBinary())
  password_hash = db.Column(db.String(128))#arbitrary password
  #token authetication for api
  token = db.Column(db.String(32), index=True, unique = True)
  token_expiration=db.Column(db.DateTime)

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
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'),primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), primary_key = True)
    agent_number = db.Column(db.Integer) #0-9, their identifier in the game
    time = db.Column(db.DateTime)

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
        return json.dumps(self.to_dict())


############
#Needs serious refator to be stateful
############


class Game(db.Model):
    '''
    A class for recording a full play of a game of The Resistance.
    '''
    #SQLAlchemy vars
    __tablename__='games'
    game_id = db.Column(db.Integer, primary_key = True)
    score = db.Column(db.Integer)
    num_players = db.Column(db.Integer)
    spies = db.Column(db.String(5)) #only populated at the end.
    rounds = db.relationship('Round',backref='game',lazy=False)
    #backrefs for rounds and missions
    
    def play(self, agents):
        if len(agents)<5 or len(agents)>10:
            raise Exception('Agent array out of range')
        #clone and shuffle agent array
        self.agents = agents.copy()
        random.shuffle(self.agents)
        self.num_players = len(agents)
        #allocate spies
        self.spies = []
        while len(self.spies) < Agent.spy_count[self.num_players]:
            spy = random.randrange(self.num_players)
            if spy not in self.spies:
                self.spies.append(spy)
        #start game for each agent        
        for agent_id in range(self.num_players):
            spy_list = self.spies.copy() if agent_id in self.spies else []
            self.agents[agent_id].new_game(self.num_players,agent_id, spy_list)
        #initialise rounds
        self.missions_lost = 0
        self.rounds = []
        #commence rounds
        leader_id = 0
        for i in range(5):
            rnd = Round()
            rnd.game = self
            self.rounds.append(rnd)
            if not self.rounds[i].play(leader_id, self.agents, self.spies, i): self.missions_lost+= 1
            for a in self.agents:
                a.round_outcome(i+1, self.missions_lost)
            leader_id = (leader_id+len(self.rounds[i].missions)) % len(self.agents)    
        for a in self.agents:
            a.game_outcome(self.missions_lost<3, self.spies)


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
RoundClass
#######################################

class Round(db.Model):
    '''
    A class for representing a full play of a round in a game of The Resistance.
    '''
    __tablename__ = 'rounds'
    round_id = db.Column(db.Integer, primary_key = True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), nullable = False)
    success = db.Column(db.Boolean)#resistance wins
    round_num = db.Column(db.Integer)
    missions = db.relationship('Mission',backref='round',lazy=False)

    def play(self, leader_id, agents, spies, rnd):
        '''
        leader_id is the current leader (next to propose a mission)
        agents is the list of agents in the game,
        spies is the list of indexes of spies in the game
        rnd is what round the game is up to 
        '''
        self.round_num = rnd
        self.missions = []
        #need to import Agent module?
        mission_size = Agent.mission_sizes[len(self.agents)][self.rnd]
        fails_required = Agent.fails_required[len(self.agents)][self.rnd]
        while len(self.missions)<5:
            team = self.agents[self.leader_id].propose_mission(mission_size, fails_required)
            mission = Mission()
            mission.round = self
            mission.run(leader_id, team, agents, spies, rnd, len(self.missions)==4)
            self.missions.append(mission)
            self.leader_id = (self.leader_id+1) % len(self.agents)
            if mission.is_approved():
                return mission.is_successful()
        return mission.is_successful()   


    def is_successful(self):
        '''
        returns true is the mission was successful
        '''
        return len(self.missions)>0 and self.missions[-1].is_successful()

    def to_dict(self):
        return {'round_id': self.round_id,
                'game_id': self.game_id,
                'success': self.success,
                'round_num': self.round_num,
                'missions': [m.to_dict() for m in missions]
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
    __tablename__ = 'missions'
    mission_id = db.Column(db.Integer, primary_key = True)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.round_id', nullable = False))
    leader = db.Column(db.Integer)
    team_string = db.Column(db.String(5))
    vote_string = db.Column(db.String(10))
    approved = db.Column(db.Boolean)
    fails = db.Column(db.String(4))
    success = db.Column(db.Boolean)

#mission.run(leader_id, team, agents, spies, rnd, len(self.missions)==4)

    def run(self, leader_id, team, agents, spies, rnd, auto_approve):    
        '''
        Runs the mission, by asking agents to vote, 
        and if the vote is in favour,
        asking spies if they wish to fail the mission
        '''
        self.leader= leader_id
        self.team_string = team
        self.votes_for = [i for i in range(len(agents)) if auto_approve or self.agents[i].vote(team, leader_id)]
        for a in agents:
            a.vote_outcome(team, leader_id, self.votes_for)
        if 2*len(self.votes_for) > len(agents):
            self.fails = [i for i in team if i in spies and agents[i].betray(team, leader_id)]
            success = len(self.fails) < Agent.fails_required[len(self.agents)][self.rnd]
            for a in agents:
                a.mission_outcome(team, leader_id, len(self.fails), success)



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

    




