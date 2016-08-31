import java.util.*;
import java.io.*;
/**
 * A Class to represent a single game of resistance
 * @author Tim French
 * */

public class Game{

  private Map<Character,Agent> players;
  private Set<Character> spies;
  private String playerString = "";
  private String spyString = "";
  private String resString = "";
  private int numPlayers = 0;
  private static final int[] spyNum = {2,2,3,3,3,4}; //spyNum[n-5] is the number of spies in an n player game
  private static final int[][] missionNum = {{2,3,2,3,3},{2,3,4,3,4},{2,3,3,4,4},{3,4,4,5,5},{3,4,4,5,5},{3,4,4,5,5}};
                                    //missionNum[n-5][i] is the number to send on mission i in a  in an n player game
  private Random rand;
  private File logFile;
  private boolean logging = false;
  private boolean started = false;



  /**
   * Creates an empty game.
   * Game log printed to stdout
   * */
  public Game(){
    init();
  }

  /**
   * Creates an empty game
   * @param logFile path to the log file
   * */
  public Game(String fName){
    logFile = new File(fName);
    logging = true;
    init();
  }

  private void init(){
    players = new HashMap<Character,Agent>();
    spies = new HashSet<Character>();
    rand = new Random();
    long seed = rand.nextLong();
    rand.setSeed(seed);
    log("Seed: "+seed);
  }

  private void log(String msg){
    if(logging){
      try{
        FileWriter log = new FileWriter(logFile);
        log.write(msg);
        log.close();
      }catch(IOException e){e.printStackTrace();}
    }
    else{
      System.out.println(msg);
    }
  }  


  /**
   * Adds a player to a game. Once a player is added they cannot be removed
   * @param a the agent to be added
   * */
  public void addPlayer(Agent a){
    if(numPlayers > 9) throw new RuntimeException("Too many players");
    else if(started) throw new RuntimeException("Game already underway");
    else{
      Character name = (char)(65+numPlayers++);
      players.put(name, a);
      log("Player "+name+" added.");
    }
  }

  /**
   * Sets up the game and informs all players of their status.
   * This involves assigning players as spies according to the rules.
   */
  public void setup(){
    if(numPlayers < 5) throw new RuntimeException("Too few players");
    else if(started) throw new RuntimeException("Game already underway");
    else{
      for(int i = 0; i<spyNum[numPlayers-5]; i++){
        char spy = ' ';
        while(spy==' ' || spies.contains(spy)){
          spy = (char)(65+rand.nextInt(numPlayers));
        }
        spies.add(spy);
      }
      for(Character c: players.keySet())playerString+=c;
      for(Character c: spies){spyString+=c; resString+='?';}
      statusUpdate(0,0);
      started= true;
    }
  }


  /**
   * Sends a status update to all players.
   * The status includes the players name, the player string, the spys (or a string of ? if the player is not a spy, the number of rounds played and the number of rounds failed)
   * @param round the current round
   * @param fails the number of rounds failed
   **/
  private void statusUpdate(int round, int fails){
    for(Character c: players.keySet()){
      if(spies.contains(c)) 
        players.get(c).get_status(""+c,playerString,spyString,round,fails);
      else 
        players.get(c).get_status(""+c,playerString,resString,round,fails);
    }
  }

  /**
   * This method picks a random leader for the next round and has them nominate a mission team.
   * If the leader does not pick a legitimate mission team (wrong number of agents, or agents that are not in the game) a default selection is given instead.
   * @param round the round in the game the mission is for.
   * @return a String containing the names of the agents being sent on the mission
   * */
  private String nominate(int round){
    Character leader = (char)(rand.nextInt(numPlayers)+65);
    int mNum = missionNum[numPlayers-5][round];
    String team = players.get(leader).do_Nominate(mNum);
    char[] tA = team.toCharArray();
    Arrays.sort(tA);
    boolean legit = tA.length==mNum;
    for(int i = 0; i<mNum; i++){
      if(!players.keySet().contains(tA[i])) legit = false;
      if(i>0 && tA[i]==tA[i-1]) legit=false;
    }
    if(!legit){
      team = "";
      for(int i = 0; i< mNum; i++) team+=(char)(65+i);
    }
    for(Character c: players.keySet())
      players.get(c).get_ProposedMission(leader+"", team);
    return team;
  }

  /**
   * This method requests votes from all players on the most recently proposed mission teams, and reports whether a majority voted yes.
   * It counts the votes and reports a String of all agents who voted in favour to the each agent.
   * @return true if a strict majority supported the mission.
   * */
  private boolean vote(){
   int votes = 0;
   String yays = "";
   for(Character c: players.keySet()){
      if(players.get(c).do_Vote()){
        votes++;
        yays+=c;
       }
    }
    for(Character c: players.keySet())
      players.get(c).get_Votes(yays);
    return (votes>numPlayers/2);  
  }

  /**
   * Polls the mission team on whetehr they betray or not, and reports the result.
   * First it informs all players of the team being sent on the mission. 
   * Then polls each agent who goes on the mission on whether or not they betray the mission.
   * It reports to each agent the number of betrayals.
   * @param team A string with one character for each member of the team.
   * @return the number of agents who betray the mission.
   * */
  public int mission(String team){
    for(Character c: players.keySet())
      players.get(c).get_Mission(team);
    int traitors = 0;
    for(Character c: team.toCharArray()){
      if(players.get(c).do_Betray()) traitors++;
    }
    for(Character c: players.keySet())
      players.get(c).get_Traitors(traitors);
    return traitors;  
  }

  /**
   * Conducts the game play, consisting of 5 rounds, each with a series of nominations and votes, and the eventual mission.
   * It logs the result of the game at the end.
   * */
  public void play(){
    int fails = 0;
    for(int round = 1; round<=5; round++){
      String team = nominate(round);
      int voteRnd = 0;
      while(voteRnd++<5 && !vote())
        team = nominate(round);
      int traitors = mission(team);
      if(traitors !=0 && (traitors !=1 || round !=4 || numPlayers<7))
        fails++;
      statusUpdate(round, fails);
      HashMap<Character,String> accusations = new HashMap<Character, String>();
      for(Character c: players.keySet())
        accusations.put(c,players.get(c).do_Accuse());
      for(Character c: players.keySet())
        for(Character a: accusations.keySet())
          players.get(c).get_Accusation(a+"", accusations.get(a));
    }
    if(fails>2) log("Government Wins! "+fails+" missions failed.");
    else log("Resistance Wins! "+fails+" missions failed.");
    log("The Government Spies were "+spyString+".");
  }

}  
        
        
        









