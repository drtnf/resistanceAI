package cits3001_2016s2;

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
  private long stopwatch = 0;


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

  /**
   * Initializes the data structures for the game
   * */
  private void init(){
    players = new HashMap<Character,Agent>();
    spies = new HashSet<Character>();
    rand = new Random();
    long seed = rand.nextLong();
    rand.setSeed(seed);
    log("Seed: "+seed);
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
   * Adds a player to a game. Once a player is added they cannot be removed
   * @param a the agent to be added
   * */
  public char addPlayer(Agent a){
    if(numPlayers > 9) throw new RuntimeException("Too many players");
    else if(started) throw new RuntimeException("Game already underway");
    else{
      Character name = (char)(65+numPlayers++);
      players.put(name, a);
      log("Player "+name+" added.");
      return name;
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
      char[] pArr = playerString.toCharArray();
      Arrays.sort(pArr);
      playerString = new String(pArr);
      char[] sArr = spyString.toCharArray();
      Arrays.sort(sArr);
      spyString = new String(sArr);
      statusUpdate(1,0);
      started= true;
      log("Game set up. Spys allocated");
    }
  }

  /** 
   * Starts a timer for Agent method calls
   * */
  private void stopwatchOn(){
    stopwatch = System.currentTimeMillis();
  }

  /**
   * Checks how if timelimit exceed and if so, logs a violation against a player.
   * @param limit the limit since stopwatch start, in milliseconds
   * @param player the player who the violation will be recorded against.
   * */
  private void stopwatchOff(long limit, Character player){
    long delay = System.currentTimeMillis()-stopwatch;
    if(delay>limit)
      log("Player: "+player+". Time exceeded by "+delay);
  }

  /**
   * Sends a status update to all players.
   * The status includes the players name, the player string, the spys (or a string of ? if the player is not a spy, the number of rounds played and the number of rounds failed)
   * @param round the current round
   * @param fails the number of rounds failed
   **/
  private void statusUpdate(int round, int fails){
    for(Character c: players.keySet()){
      if(spies.contains(c)){
        stopwatchOn(); players.get(c).get_status(""+c,playerString,spyString,round,fails); stopwatchOff(100,c);
      }
      else{ 
        stopwatchOn(); players.get(c).get_status(""+c,playerString,resString,round,fails); stopwatchOff(100,c);
      }
    }
  }

  /**
   * This method picks a random leader for the next round and has them nominate a mission team.
   * If the leader does not pick a legitimate mission team (wrong number of agents, or agents that are not in the game) a default selection is given instead.
   * @param round the round in the game the mission is for.
   * @return a String containing the names of the agents being sent on the mission
   * */
  private String nominate(int round, Character leader){
    int mNum = missionNum[numPlayers-5][round-1];
    stopwatchOn(); String team = players.get(leader).do_Nominate(mNum); stopwatchOff(1000,leader);
    char[] tA = team.toCharArray();
    Arrays.sort(tA);
    boolean legit = tA.length==mNum;
    for(int i = 0; i<mNum && legit; i++){
      if(!players.keySet().contains(tA[i])) legit = false;
      if(i>0 && tA[i]==tA[i-1]) legit=false;
    }
    if(!legit){
      team = "";
      for(int i = 0; i< mNum; i++) team+=(char)(65+i);
    }
    for(Character c: players.keySet()){
      stopwatchOn(); players.get(c).get_ProposedMission(leader+"", team); stopwatchOff(100, c);
    }
    log(leader+" nominated "+team);
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
      stopwatchOn(); 
      if(players.get(c).do_Vote()){
        votes++;
        yays+=c;
       }
      stopwatchOff(1000,c);
    }
    for(Character c: players.keySet()){
      stopwatchOn();
      players.get(c).get_Votes(yays);
      stopwatchOff(100,c);
    }
    log(votes+" votes for: "+yays);
    return (votes>numPlayers/2);  
  }

  /**
   * Polls the mission team on whether they betray or not, and reports the result.
   * First it informs all players of the team being sent on the mission. 
   * Then polls each agent who goes on the mission on whether or not they betray the mission.
   * It reports to each agent the number of betrayals.
   * @param team A string with one character for each member of the team.
   * @return the number of agents who betray the mission.
   * */
  public int mission(String team){
    for(Character c: players.keySet()){
      stopwatchOn();
      players.get(c).get_Mission(team);
      stopwatchOff(100,c);
    }
    int traitors = 0;
    for(Character c: team.toCharArray()){
      stopwatchOn();
      if(spies.contains(c) && players.get(c).do_Betray()) traitors++;
      stopwatchOff(1000,c);
    }
    for(Character c: players.keySet()){
      stopwatchOn();
      players.get(c).get_Traitors(traitors);
      stopwatchOff(100,c);
    }
    log(traitors +(traitors==1?" spy ":" spies ")+ "betrayed the mission");
    return traitors;  
  }

  /**
   * Conducts the game play, consisting of 5 rounds, each with a series of nominations and votes, and the eventual mission.
   * It logs the result of the game at the end.
   * @return the number of failed missions
   * */
  public int play(){
    int fails = 0;
    int leader = (rand.nextInt(numPlayers));
    for(int round = 1; round<=5; round++){
      String team = nominate(round, playerString.charAt(leader++%numPlayers));
      leader%=numPlayers;
      int voteRnd = 0;
      while(voteRnd++<5 && !vote())
        team = nominate(round, playerString.charAt(leader++%numPlayers));
      log(team+" elected");
      int traitors = mission(team);
      if(traitors !=0 && (traitors !=1 || round !=4 || numPlayers<7)){
        fails++;
        log("Mission failed");
      }
      else log("Mission succeeded");
      statusUpdate(round+1, fails);
      HashMap<Character,String> accusations = new HashMap<Character, String>();
      for(Character c: players.keySet()){
        stopwatchOn();
        accusations.put(c,players.get(c).do_Accuse());
        stopwatchOff(1000,c);
      }
      for(Character c: players.keySet()){
        log(c+" accuses "+accusations.get(c));
        for(Character a: players.keySet()){
          stopwatchOn();
          players.get(a).get_Accusation(c+"", accusations.get(c));
          stopwatchOff(100,c);
        }
      }  
    }
    if(fails>2) log("Government Wins! "+fails+" missions failed.");
    else log("Resistance Wins! "+fails+" missions failed.");
    log("The Government Spies were "+spyString+".");
    return fails;
  }



  static class Competitor implements Comparable{
    private Class agent;
    private String name;
    private String authors;
    public int spyWins;
    public int spyPlays;
    public int resWins;
    public int resPlays;

    public Competitor(Agent agent, String name, String authors){
      this.agent = agent.getClass();
      this.name = name;
      this.authors = authors;
    }

    public int compareTo(Object o){
      try{
        Competitor c = (Competitor) o;
        return (int)(1000*(this.winRate()-c.winRate()));
      }
      catch(Exception e){return 1;}
    }

    public Agent getAgent(){
     try{return (Agent)agent.newInstance();}
     catch(Exception e){return null;}
    }

    public String getName(){return name;}

    public String getAuthors(){return authors;}

    public void spyWin(){
      spyWins++;spyPlays++;
    }

    public void spyLoss(){
      spyPlays++;
    }

    public void resWin(){
      resWins++;resPlays++;
    }

    public void resLoss(){
      resPlays++;
    }
  
    public double spyWinRate(){
      return (1.0*spyWins)/spyPlays;
    }

    public double resWinRate(){
      return (1.0*resWins)/resPlays;
    }

    public double winRate(){
      return (1.0*(spyWins+resWins))/(spyPlays+resPlays);
    }

    public String toString(){
      return "<tr><td>"+name+
        "</td><td>"+authors+
        "</td><td>"+spyWins+
        "</td><td>"+spyPlays+
        "</td><td>"+resWins+
        "</td><td>"+resPlays+
        "</td><td>"+winRate()+
        "</td></tr>\n";
    }
  }

  public static String tournament(Competitor[] agents, int rounds){
    Random tRand = new Random();
    for(int round = 0; round<rounds; round++){
      Game g = new Game("Round"+round+".txt");
      int playerNum = 5+tRand.nextInt(6);
      for(int i = 0; i<playerNum; i++){
        int index = tRand.nextInt(agents.length);
        g.stopwatchOn();char name = g.addPlayer(agents[index].getAgent());g.stopwatchOff(1000,name);
        g.log("Player "+ agents[index].getName()+" from "+agents[index].getAuthors()+" is "+name);
      }
      g.setup();
      int fails = g.play();
      int i = 0;
      char[] spies = g.spyString.toCharArray();
      for(Character c: g.playerString.toCharArray()){
        for(Competitor cc: agents){
          if(cc.agent.isInstance(g.players.get(c))){
            if(i<spies.length && c==spies[i]){
              if (fails>2) cc.spyWin();
              else cc.spyLoss();
              i++;
            }
            else{
              if(fails>2) cc.resLoss();
              else cc.resWin();
            }
          g.log(cc.toString());
          }  
        }
      }    
    }
    Arrays.sort(agents);
    String ret = 
    "<html><body><table><tr><th>Name</th><th>Author</th><th>Spy Wins</th><th>Spy Plays</th><th>Res Wins</th><th>Res Plays</th><th>Win Rate</th></tr>";
    for(int i = 0; i< agents.length; i++)
      ret+= agents[i];
    return ret+"</table></body></html>";  
  }


  /**
   * Sets up game with random agents and plays
   **/
  public static void main(String[] args){
    /* Run a single game
    Game g = new Game();
    g.stopwatchOn();g.addPlayer(new RandomAgent());g.stopwatchOff(1000,'A');
    g.stopwatchOn();g.addPlayer(new RandomAgent());g.stopwatchOff(1000,'B');
    g.stopwatchOn();g.addPlayer(new RandomAgent());g.stopwatchOff(1000,'C');
    g.stopwatchOn();g.addPlayer(new RandomAgent());g.stopwatchOff(1000,'D');
    g.stopwatchOn();g.addPlayer(new RandomAgent());g.stopwatchOff(1000,'E');
    g.setup();
    g.play();
    */
    /*Run a tournament*/
    try{
      File f = new File("Results.html");
      FileWriter fw = new FileWriter(f);
      Competitor[] contenders = {new Competitor(new RandomAgent(),"Randy","Tim")};
      fw.write(tournament(contenders, 10));
      fw.close();
    }
    catch(IOException e){System.out.println("IO fail");}
  }

}  





        
        









