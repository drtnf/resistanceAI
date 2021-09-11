package cits3001_2021;

import java.util.*;
import java.io.*;

/**
 * A Java class for a human to play Resistance.
 * @author Tim French
 * **/


public class HumanAgent implements Agent{

  private Scanner scanner;
  private int players;
  private int[] spies;
  private String name;
  private int index;
  private boolean spy = false;
  private PrintStream out;

  public HumanAgent(String name){
    this.out = System.out;
    this.name = name;
    scanner = new Scanner(System.in);
  }  
 
  /**
   * returns an instance of this agent for testing.
   * The progam should allocate the agent's name, 
   * and can use a counter to ensure no two agents have the same name.
   * @return an instance of the agent, with the given name.
   * **/
  public static Agent init(){
    return new HumanAgent("MeatBrain");
  }

  private String getInput(){
    String s = scanner.nextLine();
    return s;
  }

  //writes to output stream with a newline
  private void write(String s){
    out.println(s);
  }

  /**
   * gets the name of the agent
   * @return the agent's name.
   * **/
  public String getName(){return name;}

  /**
   * Initialises a new game. 
   * The agent should drop their current gameState and reinitialise all their game variables.
   * @param numPlayers the number of players in the game.
   * @param playerIndex the players index in the game.
   * @param spies, the index of all the spies in the game, if this agent is a spy (i.e. playerIndex is an element of spies)
   * **/
  public void newGame(int numPlayers, int playerIndex, int[] spies){
    players = numPlayers;
    index = playerIndex;
    this.spies = spies;
    for(int i  = 0; i< spies.length; i++) 
      if(spies[i]==index) spy = true;
    write("There are "+players+" players in the game");
    write("Your index is "+index);
    if(spy){
      write("You are a spy. The spies are:");
      for(int i  = 0; i< spies.length; i++) 
        write("Player "+spies[i]);
    }
    else write("You are not a spy.");
  }

  /**
   * This method is called when the agent is required to lead (propose) a mission
   * @param teamSize the number of agents to go on the mission
   * @param failsRequired the number of agent fails required for the mission to fail
   * @return an array of player indexes, the proposed mission.
   * **/
  public int[] proposeMission(int teamSize, int failsRequired){
    write("Please propose a mission with "+teamSize+"members");
    write("The mission will require "+failsRequired+"fails to fail");
    int[] team = new int[teamSize];
    boolean[] in = new boolean[players];
    for(int i = 0; i<teamSize; i++){
      int member = -1;
      while(member < 0 ||member >= players || in[member]){
        write("next member?");
        member = Integer.parseInt(getInput());
      }
      in[member] = true;
      team[i] = member;
    }
    return team;
  }
       

  /**
   * This method is called when an agent is required to vote on whether a mission should proceed
   * @param mission the array of agent indexes who will be going on the mission.
   * @param leader the index of the agent who proposed the mission.
   * @return true is this agent votes that the mission should go ahead, false otherwise.
   * **/
  public boolean vote(int[] mission, int leader){
    char resp = 'x';
    while(resp!='Y' && resp!='N'){
      write("The mission: "+getTeamString(mission, leader)+" was proposed.");
      write("Do you approve (Y/N)?");
      resp = getInput().toUpperCase().charAt(0);
    }
    return resp=='Y';
  }


  /**
   * The method is called on an agent to inform them of the outcome of a vote, 
   * and which agent voted for or against the mission.
   * @param mission the array of agent indexes represent the mission team
   * @param leader the agent index of the leader, who proposed the mission
   * @param votes an array of booleans such that votes[i] is true if and only if agent i voted for the mission to go ahead.
   * **/
  public void voteOutcome(int[] mission, int leader, boolean[] votes){
    write("The mission: "+getTeamString(mission,leader)+" was voted upon.");
    write("The results were:");
    for(int i = 0; i<players; i++)
      write("Player "+i+" voted "+(votes[i]?"Yes.":"No."));
  }
  
       
  private String getTeamString(int[] mission){
    String teamString = "["+mission[0];
    for(int i = 1; i<mission.length; i++)
      teamString += ","+mission[i]; 
    teamString+="]";
    return teamString;
  }

  private String getTeamString(int[] team, int leader){
    return getTeamString(team)+", lead by "+leader;
  }
  
  /**
  * This method is called on an agent who has a choice to betray (fail) the mission
  * @param mission the array of agent indexes representing the mission team
  * @param leader the agent who proposed the mission
  * @return true is the agent choses to betray (fail) the mission
  * **/
  public boolean betray(int[] mission, int leader){
    char resp = 'x';
    while(resp!='Y' && resp!='N'){
      write("You are on mission: "+getTeamString(mission, leader)+".");
      write("Do you fail the mission (Y/N)?");
      resp = getInput().toUpperCase().charAt(0);
    }
    return resp=='Y';
  }

  /**
  * Informs all agents of the outcome of the mission, including the number of agents who failed the mission.
  * @param mission the array of agent indexes representing the mission team
  * @param leader the agent who proposed the mission
  * @param numFails the number of agent's who failed the mission
  * @param missionSuccess true if and only if the mission succeeded.
  * **/
  public void missionOutcome(int[] mission, int leader, int numFails, boolean missionSuccess){
    String outcome = missionSuccess? " succeeded": " failed";
    write("The mission "+getTeamString(mission, leader)+outcome+", with "+numFails+" failures");
    return;
  }

  /**
  * Informs all agents of the game state at the end of the round
  * @param roundsComplete the number of rounds played so far
  * @param roundsLost the number of rounds lost so far
  * **/
  public void roundOutcome(int roundsComplete, int roundsLost){
    write("The resistance have failed in "+roundsLost+" out of "+roundsComplete+" rounds."); 
    return;
  }
    

  /**
  * Informs all agents of the outcome of the game, including the identity of the spies.
  * @param roundsLost the number of rounds the Resistance lost
  * @param spies an array with the indexes of all the spies in the game.
  * **/
  public void gameOutcome(int roundsLost, int[] spies){
    if(roundsLost<3) write("The resistance succeeded.");
    else write("The resistance failed.");
    write("The spies were "+getTeamString(spies));
    return;
  }

}
