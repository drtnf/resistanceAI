package Agents;
import java.util.*;

/**
 * A Java interface for an agent to play in Resistance.
 * Each agent is given a single capital letter, which will be their name for the game.
 * The game actions will be encoded using strings.
 * The agent will be created entirely in a single game, and the agent must maintain its own state.
 * Methods will be used for informing agents of game events (get_ methods, must return in 100ms) or requiring actions (do_ methods, must return in 1000ms).
 * If actions do not meet the required specification, a nominated default action will be recorded.
 * @author Tim French
 * **/


public class BayesGent extends Agent{

  //As a resistance member
  //keeps a record of all possibilities
  //Assigns probabilities as follows:
  //Assumes Spies behave as follows:
    //90% nominate a team with a spy
    //90% vote for teams containing at least one spy (two for double fails)
    //90% betray if only spy in mission (except double fails)
    //40% betray if two spies in mission (90% if double fail)
    //30% betray if three spies in mission (50% if double fail)
    //20% betray if four spies in mission (30% if double fail)
    //If accusing 80% resistance, 20% spy 
  //Assume resistance behave randomly 
  //For each world (176 of them):
    //after every action apply Bayes rule to determine relative probablity.
    //Announce when more than 80% likely
    //pick teams of least likely spies
    //vote yes if >40% chance of success. (given prior probs).
    
  //As a spy
    //nominate the team that for each resistance member (6), 
        //minimises the chance of detection,
      //and increases chance of mission failure.
      //Assume other spies behave as above
      //Accuse most likely resistance members

  /**
   * Reports the current status, inlcuding players name, the name of all players, the names of the spies (if known), the mission number and the number of failed missions
   * @param name a string consisting of a single letter, the agent's names.
   * @param players a string consisting of one letter for everyone in the game.
   * @param spies a String consisting of the latter name of each spy, if the agent is a spy, or n questions marks where n is the number of spies allocated; this should be sufficient for the agent to determine if they are a spy or not. 
   * @param mission the next mission to be launched
   * @param failures the number of failed missions
   * */
  public void get_status(String name, String players, String spies, int mission, int failures);
  
  /**
   * Nominates a group of agents to go on a mission.
   * If the String does not correspond to a legitimate mission (<i>number</i> of distinct agents, in a String), 
   * a default nomination of the first <i>number</i> agents (in alphabetical order) will be reported, as if this was what the agent nominated.
   * @param number the number of agents to be sent on the mission
   * @return a String containing the names of all the agents in a mission
   * */
  public String do_Nominate(int number);

  /**
   * Provides information of a given mission.
   * @param leader the leader who proposed the mission
   * @param mission a String containing the names of all the agents in the mission 
   **/
  public void get_ProposedMission(String leader, String mission);

  /**
   * Gets an agents vote on the last reported mission
   * @return true, if the agent votes for the mission, false, if they vote against it.
   * */
  public boolean do_Vote();

  /**
   * Reports the votes for the previous mission
   * @param yays the names of the agents who voted for the mission
   **/
  public void get_Votes(String yays); 

  /**
   * Reports the agents being sent on a mission.
   * Should be able to be infered from tell_ProposedMission and tell_Votes, but incldued for completeness.
   * @param mission the Agents being sent on a mission
   **/
  public void get_Mission(String mission);

  /**
   * Agent chooses to betray or not.
   * @return true if agent betrays, false otherwise
   **/
  public boolean do_Betray();

  /**
   * Reports the number of people who betrayed the mission
   * @param traitors the number of people on the mission who chose to betray (0 for success, greater than 0 for failure)
   **/
  public void get_Traitors(int traitors);


  /**
   * Optional method to accuse other Agents of being spies. 
   * Default action should return the empty String. 
   * Convention suggests that this method only return a non-empty string when the accuser is sure that the accused is a spy.
   * Of course convention can be ignored.
   * @return a string containing the name of each accused agent. 
   * */
  public String do_Accuse();

  /**
   * Optional method to process an accusation.
   * @param accuser the name of the agent making the accusation.
   * @param accused the names of the Agents being Accused, concatenated in a String.
   * */
  public void get_Accusation(String accuser, String accused);

}
