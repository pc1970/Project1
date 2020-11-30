package game;
/**
 *
 * @author 
 */
public class Weapon {
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
    
    public Weapon( String name, int power ) {
        this.name = name;
        this.power = power;
    }

    //   public void setUpWeapons(HashMap<String, Weapon> weapons){
    //       Weapon w = new Weapon();
    //       w.setName("Sword");
    //       w.setPower(100);
    //       weapons.put("Sword",w);
    //       w = new Weapon();
    //       w.setName("Bomb");
    //       w.setPower(1000);
    //       weapons.put("Bomb",w);
    //       w = new Weapon();
    //       w.setName("Bat");
    //       w.setPower(500);          
    //       weapons.put("Bat",w);
    //  }
}
