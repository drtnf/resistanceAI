# resistanceAI
AI platform for the card game resistance.

# Description
This projects aims to provide a set of java classes and interface to facilliate agents playing Don Eskridge's card game: Resistance.

# Getting started

## Python

To build an agent in python, you should copy the template provided in the `random_agent.py` module. 
That is, you should subclass the Agent class (defined in the `agent.py` module) and fill in the methods there.
To manage agents in ad-hoc tournaments, it is recommended that you incorporate your student number in the module containing your agent code,
and have all your code in the one module.

To run the contest, you should edit the `__main__.py` file to import you agent class, and add your agents to the agent array.

The basic command line game code can then be executed using the command:

`python3 resistance`

called from `src-py` (the directory containing the `resistance` package).

#Rules

##Rules - resistance

Resistance is a multiplayer game, requiring at least 5 players. One third of the players are selected to be government spies, and the remaining players are memebers of the resistance.
The spies know who all the other spies are, but the resistance members are unable to distinguish the spies.

The game play consists of 5 rounds. In each round, a leader is randomly selected. That leader then proposes a group to be sent on a mission. 
The size of the group depends on the numbers of players and and the round. All players vote on the group. 
If players vote to accept the group, the players are sent on a mission. If players vote to reject a group, a new leader is randomly selected and the process repeats.
If five groups are rejected in a row, the mission fails.
When a group of players is selected for a mission, if one person betrays the group the mission will fail, otherwise it will succeed. 
Only spies can betray the group, but they may choose not to. 
The mission itself simply involves the players on the mission choosing whether or not to betry the group. 
This is done privately, and the only public information released is how many people betrayed the group.

If at least 3 missions succeed, the resistance wins. Otherwise the government wins.

##Rules - AI bots
1. AI bots must implement the provided agent interface, and we will add restrictions for the amount of computation, and system resources they can use.
5. Agents should have a parameterless constructor
5. Java classes should have unique names. Please append your student number to the end of each class name to avoid clashes.
6. The tournament will will be a selection of random games. Game.java has a sample tournament file.
7. Agents will be randomly selected to play in games of between 5 and 10 players. There may be two or more instances of the one agent in a game.
8. There will be a large number of plays to give all agents a chance to play both sides.
9. Agents will be ranked on the percentage of games they win, regardless of whetehr they are a spy or a resistance member.
10. Any attempt to cheat will result in immediate disqualification.
11. Any Agent who crashes, or gets stuck in an infinite loop will be removed from the tournament.
12. Agents who go over time, will be penalised or removed from the competition.

Good luck.


