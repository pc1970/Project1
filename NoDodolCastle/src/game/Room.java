package game;
public class Room {
    static gameMaster gm=new gameMaster();
      public static void characteristics(){
        System.out.println("Player Characteristics are:");
        System.out.println("Name: "+gameMaster.name);
        System.out.println("Demage: "+gameMaster.lowerDamage+" to "+gameMaster.upperDamage);
        System.out.println("Defence: "+gameMaster.defense);
        System.out.println("HP: "+gameMaster.hp);
    }
}