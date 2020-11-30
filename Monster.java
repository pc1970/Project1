package game;
import java.util.HashMap;

/**
 *
 * @author 
 */
@SuppressWarnings("unused")
public class Monster {
    
    int power;
    String name;
    
    public void setPower(int power){
        this.power = power;
    }
    public void setName(String name){
        this.name= name;
    }
    public int getPower(){
        return this.power;
    }
    public String getName(){
        return this.name;
    }
    
    public Monster( String name, int power ) {
        this.name = name;
        this.power = power;
    }

    //   public void setUpMonsters(HashMap<String, Monster> monsters){
    //       Monster m = new Monster();
    //       m.setName("Devil");
    //       m.setPower(1900);
    //       monsters.put("Devil",m);
    //       m = new Monster();
    //       m.setName("Daemon");
    //       m.setPower(1300);
    //       monsters.put("Daemon",m);
    //       m = new Monster();
    //       m.setName("Bad");
    //       m.setPower(1200);          
    //       monsters.put("Bad",m);
    //  }
}
