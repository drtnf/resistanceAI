package cits3001_2016s2;


  public class Competitor implements Comparable{
    public Class agent;
    public String name;
    public String authors;
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
        "</td><td>"+spyWinRate()+
        "</td><td>"+resWinRate()+
        "</td></tr>\n";
    }
  }
