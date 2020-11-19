/*
 * Better to change this class name. I do not know .....................
 * 
 * 
 */

public class Hero {
    static gameMaster gm=new gameMaster();
    Room r1=new Room();
    public void ActionMethod()
        {
            gameMaster.name = "The Hero";
            gameMaster.lowerDamage = 2;
            gameMaster.upperDamage = 4;        
            gameMaster.defense = 1;
            gameMaster.hp = 20;
            gameMaster.orbPower = 0;
            gameMaster.checker = 0;
            gameMaster.MonsterDamage = 15;
            gameMaster.day = 1;
            Room.characteristics();
        }
}
