import random

class Agent:
    '''An abstract super class for an agent in the game The Resistance'''

    def __init__(self):
        '''
        Initialises the agent. 
        You can add configuration parameters etc here,
        but the default code will always assume a 0-parameter constructor.
        The agent will persist between games to allow for long-term learning etc.
        '''
        #game parameters for agents to access
        #e.g. self.mission_size[8][3] is the number to be sent on the 3rd mission in a game of 8
        self.mission_sizes = {
                5:[2,3,3,3,2], \
                6:[3,3,3,3,3]
                }
        #e.g. self.betrayals_required[8][3] is the number of betrayals required for the 3rd mission in a game of 8 to fail
        self.betrayals_required = {
                5:[1,1,1,1,1], \
                6:[1,1,1,1,1]
                }
        #etc

    def new_game(self, number_of_players, player_number, spies):
        '''
        initialises the game, informing the agent of the number_of_players, 
        the player_number (an id number for the agent in the game),
        and a list of agent indexes, which is the set of spies if this agent is a spy,
        or an empty list if this agent is not a spy.
        '''
        pass

    def propose_mission(team_size, betrayals_required = 1):
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned. 
        betrayals_required are the number of betrayals required for the mission to fail.
        '''
        pass

    def vote(mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        pass

    def vote_outcome(mission, proposer, votes):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
        pass

    def betray(mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The method should return True if this agent chooses to betray the mission, and False otherwise. 
        Only spies are permitted to betray the mission (I think). 
        '''
        pass

    def mission_outcome(mission, proposer, betrayals, mission_success):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        betrayals is the number of people on the mission who betrayed the mission, 
        and mission_success is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It iss not expected or required for this function to return anything.
        '''
        pass

    def round_outcome(rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''
        pass
    
    def game_outcome(spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        pass

class RandomAgent(agent):        
    '''A basic implementation of a random agent in the game The Resistance'''

    def __init__(self):
        '''
        Initialises the agent. 
        '''
        pass

    def new_game(self, number_of_players, player_number, is_spy):
        '''
        initialises the game, informing the agent of the 
        number_of_players, the player_number (an id number for the agent in the game),
        and a boolean, is_spy, which is true is the agent is a spy
        '''
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.is_spy = is_spy

    def propose_mission(number    


