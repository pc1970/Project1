package game;
/**
*
* @author 
*/
/*
* To change this license header, choose License Headers in Project Properties.
* To change this template file, choose Tools | Templates
* and open the template in the editor.
*/

public class Multiplayer {
   public gameMaster gm=new gameMaster();
   
   public String username;
   public Multiplayer(String username){
       this.username = username;
   }
   
   Room r1=new Room();
   public void ActionMethod()
       {
           gm.name = this.username;
           gm.lowerDamage = 2;
           gm.upperDamage = 4;        
           gm.defense = 1;
           gm.hp = 20;
           gm.orbPower = 0;
           gm.checker = 0;
           gm.MonsterDamage = 15;
           gm.day = 1;
           Room.characteristics();
       }
}


