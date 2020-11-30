package game;
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
           gameMaster.name = this.username;
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


