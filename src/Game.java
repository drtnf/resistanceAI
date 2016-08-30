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
  private static final int[] spyNum = {2,2,3,3,3,4} //spyNum[n-5] is the number of spies in an n player game
  private static final int[][] missionNum = {{2,3,2,3,3},{2,3,4,3,4},{2,3,3,4,4},{3,4,4,5,5},{3,4,4,5,5},{3,4,4,5,5}} 
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
  public Game(String logFile){
    logFile = new File(logFile);
    logging = true;
    init();
  }

  private void init(){
    players = new HashMap<Character,Agent>();
    spies = new HashSet<Character>();
    resistance = new HashSet<Character>();
    rand = new Random();
    long seed = rand.nextLong();
    rand.setSeed(seed);
    log("\n"+LocalDateTime.now()+"\nSeed: "+seed);
  }

  private void log(String msg){
    if(logging){
      try{
        FileWriter log = new FileWriter(logFile);
        log.write(msg);
        FileWriter.close();
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
      String name = ""+((char)(65+numPlayers++));
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
      for(i = 0; i<spyNum[numPlayers-5]; i++){
        char spy = ' ';
        while(spy==' ' || spies.contains(spy)){
          spy = (char)(65+rand.nextInt(numPlayers));
        }
        spies.add(spy);
      }
      for(Character c in players.keys())playerString+=c;
      for(Character c in players.spies()){spyString+=c; resString+='?';}
      statusUpdate(0,0);
      started= true;
    }
  }

  private void statusUpdate(int round, int fails){
    for(Character c in players.keys()){
      if(spies.contains(c)) 
        players.get(c).tell_status(""+c,playerString,spyString,round,fails);
      else 
        players.get(c).tell_status(""+c,playerString,resString,round,fails);
    }
  }

  public String nominate(int round){
    Character leader = (char)(rand.nextInt(numPlayers)+65);
    mNum = missionNum[numPlayers-5][round];
    String team = players.get(leader).do_Nominate(mNum);
    
    for(char c in team.toArray()){
      


  }

  public boolean vote(String team){

  }

  public int mission(String team){

  }

  public void play(){
    int fails = 0;
    for(int round = 1; round<=5; round++){
      Set<Character>  team = nominate(round);
      voteRnd = 0
      while(voteRnd++<5 && !vote())
        team = nominate(rnd);
      int traitors = mission(team);
      if(traitors !=0 && (traitors !=1 || round !=4 || numplayers<7))
        fails++;
      statusUpdate(int round, int fails);
    }
    if(fails>2) log("Government Wins! "+fails+" missions failed.");
    else log("Resistance Wins! "+fails+" missions failed.");
    log("The Government Spies were "+spyString+".");
  }

}  
        
        
        









