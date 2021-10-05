package cits3001_2021;


import java.util.*;
import java.io.*;
/**
 * A Class to represent a single game of resistance
 * @author Tim French
 * */

public class Game{

  private Agent[] players;
  private int[] spies;
  private int leader;
  private Round[] rounds;
  private int round;
  private static final int[] spyNum = {2,2,3,3,3,4}; //spyNum[n-5] is the number of spies in an n player game
  private static final int[][] missionNum = {{2,3,2,3,3},{2,3,4,3,4},{2,3,3,4,4},{3,4,4,5,5},{3,4,4,5,5},{3,4,4,5,5}};
                                    //missionNum[n-5][i] is the number to send on mission i in a  in an n player game
  private Random rand;
  private RandomAgent backup;
  private File logFile;
  private boolean logging = false;
  private boolean started = false;
  private long stopwatch = 0;

  private static final int failsRequired(int playerNum, int round){
    return (playerNum>6 && round==4)?2:1;
  }

  /**
   * Creates an empty game.
   * Game log printed to stdout
   * */
  public Game(Agent[] players){
    init(players);
  }

  /**
   * Creates an empty game
   * @param logFile path to the log file
   * */
  public Game(String fName, Agent[] players){
    logFile = new File(fName);
    logging = true;
    init(players);
  }

  private Agent[] shuffle(Agent[] players){
    Agent[] shuffle = players.clone();
    for(int i = 0; i<players.length; i++){
      int next = i + rand.nextInt(players.length-i);
      Agent n = shuffle[next];
      shuffle[next] = shuffle[i];
      shuffle[i] = n;
    }
    return shuffle;
  }

  /**
   * Initializes the data structures for the game
   * */
  private void init(Agent[] agents){
    rand = new Random();
    long seed = rand.nextLong();
    rand.setSeed(seed);
    log("Seed: "+seed);
    if(agents.length < 5) throw new RuntimeException("Too few players");
    this.players = shuffle(agents);
    leader = 0;
    this.spies = new int[spyNum[players.length-5]];
    boolean[] spying = new boolean[players.length];
    for(int i = 0; i<spyNum[players.length-5]; i++){
      int spy = -1;
      while(spy ==-1 || spying[spy]){
        spy = rand.nextInt(players.length);
      }
      spying[spy] = true;
      spies[i] = spy;
    }
    for(int i = 0; i<players.length; i++){
      int[] spyCopy = new int[0];
      if(spying[i]) spyCopy = spies.clone();
      players[i].newGame(players.length, i, spyCopy);
    }
    log("Game set up. Spys allocated");
    //allocate RandomAgent to substitute bad moves
    backup = new RandomAgent("backup");
    backup.newGame(players.length, 0, spies);
    rounds = new Round[5];
    for(round = 0; round<5; round++)
      rounds[round] = new Round();
    for(int i = 0; i< players.length; i++)
      players[i].gameOutcome(5-getScore(), spies.clone());
    log("Game complete: Resistance "+(getScore()>2?"successful.":"failed."));
    log("The spies were: "+teamString(spies));
  }

  public int getScore(){
    int score = 0;
    for(int i = 0; i< round; i++)
      if(rounds[i].successful())score++;
    return score;
  }

  public String teamString(int[] team){
    String str = "["+team[0];
    for(int i  = 1; i<team.length; i++)
      str+=","+team[i];
    return str+"]";  
  }

  /**
   * Writes the String to the log file
   * @param msg the String to log
   * */
  private void log(String msg){
    if(logging){
      try{
        FileWriter log = new FileWriter(logFile, true);
        log.write(msg);
        log.close();
      }catch(IOException e){e.printStackTrace();}
    }
    System.out.println(msg);
  }  



  /** 
   * Starts a timer for Agent method calls.
   * Not used here, but can be accessed for investigating efficiency.
   * */
  private void stopwatchOn(){
    stopwatch = System.currentTimeMillis();
  }

  /**
   * Checks how if timelimit exceed and if so, logs a violation against a player.
   * @param limit the limit since stopwatch start, in milliseconds
   * @param player the player who the violation will be recorded against.
   * */
  private void stopwatchOff(long limit, int player){
    long delay = System.currentTimeMillis()-stopwatch;
    if(delay>limit)
      log("Player: "+player+". Time exceeded by "+delay);
  }

  class Mission{
    private int missionLead;
    private int fails2Fail;
    private int[] team;
    private boolean[] vote;
    private boolean[] fails;

    public Mission(){
      missionLead = leader++;
      leader = leader%players.length;
      int teamSize = missionNum[players.length-5][round];
      fails2Fail = failsRequired(players.length, round);
      team = players[missionLead].proposeMission(teamSize, fails2Fail);
      if(!teamOk(team)){
        team  = backup.proposeMission(teamSize, fails2Fail);
        log("Invalid mission: "+teamString(team)+" proposed.");
        log("Random mission substituted.");
      }
      log("Mission: "+teamString(team)+" proposed by "+missionLead);
      vote = new boolean[players.length];
      String voteString = "";      
      for(int i = 0; i<players.length; i++)
        if(vote[i] = players[i].vote(team.clone(), missionLead)) voteString+=i+" "; 
      for(int i = 0; i< players.length; i++)
        players[i].voteOutcome(team, missionLead, vote.clone());
      if(approved()){
        log("Mission approved, votes for: "+voteString);
        fails = new boolean[players.length];
        int failNum = 0;
        for(int i = 0; i<team.length; i++)
          if(isSpy(team[i]) && (fails[team[i]] = players[team[i]].betray(team.clone(), missionLead))) failNum++;
        for(int i = 0; i<players.length; i++)
          players[i].missionOutcome(team.clone(), missionLead, failNum, isSuccess());
        log("Mission "+(isSuccess()?"succeeded":"failed")+" with "+failNum+" fails.");
      }
      else log("Mission not approved, votes for: "+voteString);
    }

    //helper method to report if agent's are spies.
    boolean isSpy(int agent){
      boolean spy = false;
      for(int i = 0; i< spies.length; i++)
        spy = spy || spies[i]==agent;
      return spy;
    }

    public boolean approved(){
      int voteNum = 0;
      for(int i = 0; i<players.length; i++)
        if(vote[i])voteNum++;
      return 2*voteNum > players.length;
    } 

    public int[] getTeam(){return team.clone();}

    public int getLeader(){return missionLead;}

    public boolean[] getVotes(){return vote.clone();}

    public boolean isSuccess(){
      int failNum = 0;
      for(int i = 0; i<team.length; i++)
        if(!approved() || fails[team[i]]) failNum++;
      return failNum<fails2Fail;
    }

    public boolean teamOk(int[] team){
      boolean[] in = new boolean[players.length];
      boolean ok = team.length==missionNum[players.length-5][round];
      for(int i =0; i<team.length; i++){
        ok = ok && team[i]>=0 && team[i]<players.length && !in[team[i]];
        in[team[i]] = true;
      }
      return ok;
    }

  }

  /**
   * An inner class for managing a round.
   * Like Mission, it is immutable after creation.
   * **/
  class Round{
    Mission[] missions;
    int mNum;
     
    public Round(){
      missions = new Mission[5];
      mNum = 0;
      missions[0] = new Mission();
      while(mNum<4 && !missions[mNum].approved())
        missions[++mNum] = new Mission();
      for(int i = 0; i<players.length; i++)
        players[i].roundOutcome(round+1, round+1-getScore());
      log("Resistance "+(successful()?"won":"lost")+" round "+(round+1));
      log((getScore()+(successful()?1:0)) + " rounds of "+(round+1)+" successful.");
    }

    public boolean successful(){
      return missions[mNum].approved() && missions[mNum].isSuccess();
    }

    public Mission[] getMissions(){
      return missions.clone();
    }
  }


  /**
   * Sets up game with random agents and plays
   **/
  public static void main(String[] args){
    Agent[] agents = {RandomAgent.init(),
      RandomAgent.init(), 
      RandomAgent.init(),
      RandomAgent.init(), 
      RandomAgent.init()};
    Game game = new Game(agents);

  }    
  

}  











