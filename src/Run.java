import cits3001_2016s2.*;
import sYourStudentNumber.*;

import java.util.*;
import java.io.*;

public class Run{

 public static void main(String args[]){

  try{
      File f = new File("Results.html");
      FileWriter fw = new FileWriter(f);
      Competitor[] contenders = {
        new Competitor(new cits3001_2016s2.RandomAgent(),"Randy","Tim"),
        new Competitor(new sYourStudentNumber.RandomAgent(),"Brandy","Tim")
        };
      fw.write(Game.tournament(contenders, 500));
      fw.close();
    }
    catch(IOException e){System.out.println("IO fail");}
  }

}  


