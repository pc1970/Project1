package game;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Random;
import java.util.Scanner;

/*
 * 
 * 
 * open the template in the editor.
 */

/**
 *
 * @author CITE-N
 */
public class Action {
    static gameMaster gm=new gameMaster();
     public static Dungeon d=new  Dungeon();
      public static Action a=new Action();
  public static void townMenu(Scanner sc,Random rand){
        outer2:
        while(true){
        System.out.println("NoDodol's Menu"); 
        System.out.println("Day"+gameMaster.day+": \nYou are in NoDodol's Castle.");
        System.out.println("1) View character.");
        System.out.println("2) View map.");
        System.out.println("3) Move.");
        System.out.println("4) Reset.");
        System.out.println("5) Save Game.");
        System.out.println("6) Exit Game.");
        System.out.println("Enter choice.");
        int againOption = sc.nextInt();
        if(againOption==1){       
        //characteristics();
        continue outer2;
        }
        else if(againOption==2){
          
            System.out.println("\nThe Map is:");
            Dungeon.map();
            continue outer2;
        }
        else if(againOption==3){
            //System.out.println("Before Updating Day : "+gm.day);
            gameMaster.day++;
            //System.out.println("After Updating Day : "+gm.day);
            System.out.println("Day"+gameMaster.day+": You are in the Castle.\nEncounter!- Monster");
            gameMaster.checkerForDamage = 1;
                                  
               move(sc,rand);                
               gameMaster.combatMenu(sc,rand);
                break;
        }
        else if(againOption==4){
            gameMaster.reset();
        }
        else if(againOption==5){
            int index = 0;
            for(int i=0;i<64;i++){
                if(gameMaster.tableValues[i]=="H"){
                    index=i;
                }
            }
          
          String str9 = Integer.toString(index)+"\n";
         int dayInteger = gameMaster.day;
        String str1 = Integer.toString(dayInteger)+"\n";
        int hpInteger = gameMaster.hp;
        String str2 = Integer.toString(hpInteger)+"\n";
        int defenceInteger = gameMaster.defense;
        String str3 = Integer.toString(defenceInteger)+"\n";
        int lDamageInteger = gameMaster.lowerDamage;
        String str4 = Integer.toString(lDamageInteger)+"\n";
        int uDamageInteger = gameMaster.upperDamage;
        String str5 = Integer.toString(uDamageInteger)+"\n";
        
        String savingData = str9+str1+str2+str3+str4+str5;
         try {
      FileWriter myWriter = new FileWriter("data.txt");
      myWriter.write(savingData);
      myWriter.close();
      System.out.println("Game is Saved.");
      return;      
    } catch (IOException e) {
      System.out.println("An error occurred.");
      e.printStackTrace();
    }
        }
        else {
        System.out.println("Do You want to play again or not.");
        System.out.println("1) play again");
        System.out.println("2) exit");
        
        int option10 = sc.nextInt();
        if(option10==1){
        extracted1();
        gameMaster.lowerDamage = 2;
        gameMaster.upperDamage = 4;        
        gameMaster.defense = 1;
        gameMaster.hp = 20;
        gameMaster.orbPower = 0;
        gameMaster.checker = 0;
        gameMaster.MonsterDamage = 15;
        gameMaster.day = 1;
            townMenu(sc,rand);
        }
        else{
        System.out.println("Game Ended.");            
         System.exit(0);
         break;
        }
                     
        }
        
        }
    }
private static String extracted1() {
	return extracted1();
}
public static void attack(Random rand,Scanner sc){
                
                if( gameMaster.upperDamage!=0){
                    gameMaster.upperDamage = gameMaster.lowerDamage+rand.nextInt(gameMaster.upperDamage-gameMaster.lowerDamage+1);
                }
                if(gameMaster.lowerDamage!=0){
                    gameMaster.lowerDamage = rand.nextInt(gameMaster.lowerDamage);            
                }
                if(gameMaster.defense!=0){
                    gameMaster.defense = rand.nextInt(gameMaster.defense);
                }
                
                int newhp = gameMaster.hp;
                if(gameMaster.hp!=0){
                gameMaster.hp = rand.nextInt(gameMaster.hp);
                }
                
                int finalhp= newhp-gameMaster.hp;
                if(gameMaster.MonsterDamage!=0){
                	gameMaster.MonsterDamage = rand.nextInt(gameMaster.MonsterDamage);
                }
                
                if(gameMaster.orbPower!=1){
                    System.out.println("You do not have the Orb of Power - the Monster is immune! ");
                }
                System.out.println("Player's HP: "+gameMaster.hp);
                System.out.println("MonsterDamage's HP: "+gameMaster.MonsterDamage);
                
                if(gameMaster.hp!=0){
                 System.out.println("You deal "+finalhp+" damage to the Monster");
                System.out.println("Oouch the Monster hit you for "+gameMaster.MonsterDamage+" damage.\nEncounter!- Monster");
               
                if(gameMaster.orbPower==1 && gameMaster.MonsterDamage==0){
                System.out.println("You deal "+gameMaster.MonsterDamage+" damage to the Monster ");
                System.out.println("The Monster is dead! You are victorious! ");
                System.out.println("Congratulations, you have defeated the Dungeon Monster! ");
                System.out.println("The world is saved! You win!  ");
                System.out.println("You Won Fight in  "+gameMaster.day+" days");                
                }
                System.out.println("Demage: "+gameMaster.lowerDamage+" to "+gameMaster.upperDamage);
                System.out.println("Defence: "+gameMaster.defense);
                System.out.println("HP: "+gameMaster.hp);
                  
                }
                
                else{                
                System.out.println("Do You want to play again or not.");
                System.out.println("1) play again");
                System.out.println("2) exit");
               
                int option3 = sc.nextInt();
                if(option3==1){
                gameMaster.name = "The Hero";
                gameMaster.lowerDamage = 2;
                gameMaster.upperDamage = 4;        
                gameMaster.defense = 1;
                gameMaster.hp = 20;
                gameMaster.orbPower = 0;
                gameMaster.checker = 0;
                gameMaster.MonsterDamage = 15;
                gameMaster.day = 1;
                  Action.townMenu(sc,rand);
                }
                else{
                System.out.println("Game Ended.");            
                 System.exit(0);
                }
                
                }
    
    }
       public static void move(Scanner sc,Random rand){
        outer3:
        while(true){
        int index = 0;
        int checkingIndex = 0;
        System.out.println("W = up; A = left; S = down; D = right ");
        char move = sc.next().charAt(0);
        System.out.println("Your Move:");        
        System.out.println(move);
        
        for(int i=0;i<64;i++){
                if(gameMaster.tableValues[i]=="H" || gameMaster.tableValues[i]=="H/T"){
                    index = i;
                    break;
                }
         }

          
        if (move == 'a') {            
            if(index!=0){
            checkingIndex = index-1;
            
            if(gameMaster.tableValues[checkingIndex] == "T"){
                gameMaster.tableValues[checkingIndex]="H/T";
                gameMaster.tableValues[index] = "T";
                System.out.println("You are in the Dungeon! ");
                break;
            }
            
         else if(gameMaster.tableValues[checkingIndex]=="O"){             
             System.out.println("You found the Orb of Power! ");
             System.out.println("Your attack increases by 5! ");
             System.out.println("Your defence increases by 5!  ");
             System.out.println("Day"+gameMaster.day+": You are in the Castle.\nEncounter!- Monster");
             gameMaster.upperDamage = gameMaster.upperDamage+5;
             gameMaster.lowerDamage = gameMaster.lowerDamage+5;
             gameMaster.defense = gameMaster.defense+5;
             gameMaster.hp = gameMaster.hp+5;
             gameMaster.tableValues[checkingIndex]="H";
             gameMaster.tableValues[index]= " ";
             gameMaster.orbPower = 1;
             break;
         }
         else{
             if(gameMaster.checkerForDamage==1){
                 if(gameMaster.upperDamage!=0){
                    gameMaster.upperDamage = gameMaster.lowerDamage+rand.nextInt(gameMaster.upperDamage-gameMaster.lowerDamage+1);
                }
                if(gameMaster.lowerDamage!=0){
                    gameMaster.lowerDamage = rand.nextInt(gameMaster.lowerDamage);            
                }
                if(gameMaster.defense!=0){
                    gameMaster.defense = rand.nextInt(gameMaster.defense);
                }
                
                if(gameMaster.hp!=0){
                gameMaster.hp = rand.nextInt(gameMaster.hp);
                }
                
            if(gameMaster.hp!=0){
            gameMaster.tableValues[index]= " ";
            gameMaster.tableValues[checkingIndex]="H"; 
            System.out.println("Day"+gameMaster.day+": You are in the Castle.\nEncounter!- Monster");
            gameMaster.orbPower = 0;
            break;
            }
            else{
            System.out.println("Sorry You are defeated by the Monster");
            System.out.println("you hp is zero");
            System.out.println("Do You want to play again or not.");
                System.out.println("1) play again");
                System.out.println("2) exit");
                
                int option4 = sc.nextInt();
                if(option4==1){
                gameMaster.name = "The Hero";
                gameMaster.lowerDamage = 2;
                gameMaster.upperDamage = 4;        
                gameMaster.defense = 1;
                gameMaster.hp = 20;
                gameMaster.orbPower = 0;
                gameMaster.checker = 0;
                gameMaster.MonsterDamage = 15;
                gameMaster.day = 1;
                  Action.townMenu(sc,rand);
                }
                else{
                System.out.println("Game Ended.");            
                 System.exit(0);
                }
            }
            
            }
            
              else{
             gameMaster.tableValues[index]= " ";
            gameMaster.tableValues[checkingIndex]="H";             
            System.out.println("Day"+gameMaster.day+": You are in the Castle.\nEncounter!- Monster");
            gameMaster.orbPower = 0;
            break;
             }
                        
         }
        }
        
        else{
           System.out.println("Sorry you cannot escape the Dungeon! "); 
           continue outer3;
        }
    }
         
        else if (move == 'd') {
            if(index!=63){
            checkingIndex = index+1;
                  if(gameMaster.tableValues[checkingIndex] == "T"){
                gameMaster.tableValues[checkingIndex]="H/T";
                gameMaster.tableValues[index] = "T";
                System.out.println("You are in the Dungeon! ");
                break;
            }
         else if(gameMaster.tableValues[checkingIndex]=="O"){             
             System.out.println("You found the Orb of Power! ");
             System.out.println("Your attack increases by 5! ");
             System.out.println("Your defence increases by 5!  ");
             System.out.println("Day"+gameMaster.day+": You are in the Castle.\nEncounter!- Monster");
             gameMaster.upperDamage = gameMaster.upperDamage+5;
             gameMaster.lowerDamage = gameMaster.lowerDamage+5;
             gameMaster.defense = gameMaster.defense+5;
             gameMaster.hp = gameMaster.hp+5;
             gameMaster.tableValues[index]= " ";
             gameMaster.tableValues[checkingIndex]="H";
             gameMaster.orbPower = 1;
             break;
         }
                  else{
             if(gameMaster.checkerForDamage==1){
                            if(gameMaster.upperDamage!=0){
                    gameMaster.upperDamage = gameMaster.lowerDamage+rand.nextInt(gameMaster.upperDamage-gameMaster.lowerDamage+1);
                }
                if(gameMaster.lowerDamage!=0){
                    gameMaster.lowerDamage = rand.nextInt(gameMaster.lowerDamage);            
                }
                if(gameMaster.defense!=0){
                    gameMaster.defense = rand.nextInt(gameMaster.defense);
                }
                
                if(gameMaster.hp!=0){
                gameMaster.hp = rand.nextInt(gameMaster.hp);
                }
            if(gameMaster.hp!=0){
            gameMaster.tableValues[index]= " ";
            gameMaster.tableValues[checkingIndex]="H"; 
            System.out.println("Day"+gameMaster.day+": You are in the Castle.\nEncounter!- Monster");
            gameMaster.orbPower = 0;
            break;
            }
            else{
            System.out.println("Sorry You are defeated by the Monster");
            System.out.println("you hp is zero");
        System.out.println("Do You want to play again or not.");
        System.out.println("1) play again");
        System.out.println("2) exit");
        
        int option5 = sc.nextInt();
        if(option5==1){
        gameMaster.name = "The Hero";
        gameMaster.lowerDamage = 2;
        gameMaster.upperDamage = 4;        
        gameMaster.defense = 1;
        gameMaster.hp = 20;
        gameMaster.orbPower = 0;
        gameMaster.checker = 0;
        gameMaster.MonsterDamage = 15;
        gameMaster.day = 1;
            Action.townMenu(sc,rand);
        }
        else{
        System.out.println("Game Ended.");            
         System.exit(0);
        }
         
            
            }
            
            }
              else{
             gameMaster.tableValues[index]= " ";
            gameMaster.tableValues[checkingIndex]="H"; 
            System.out.println("Day"+gameMaster.day+": You are in the Castle.\nEncounter!- Monster");
            gameMaster.orbPower = 0;
            break;
             }
                        
         }
        }
        else{
           System.out.println("Sorry you cannot escape the Dungeon! "); 
           continue outer3;
        }
    }
        
        else if (move == 'w') {
            if(index!=0 && index!=1 && index!=2 && index!=3 && index!=4 && index!=5 && index!=6 && index!=7){
            checkingIndex = index-8;
               if(gameMaster.tableValues[checkingIndex] == "T"){
                gameMaster.tableValues[checkingIndex]="H/T";
                gameMaster.tableValues[index] = "T";
                System.out.println("You are in the Dungeon! ");
                break;
            }
         else if(gameMaster.tableValues[checkingIndex]=="O"){             
             System.out.println("You found the Orb of Power! ");
             System.out.println("Your attack increases by 5! ");
             System.out.println("Your defence increases by 5!  ");
             System.out.println("Day"+gameMaster.day+": You are in the Castle.\nEncounter!- Monster");
             gameMaster.upperDamage = gameMaster.upperDamage+5;
             gameMaster.lowerDamage = gameMaster.lowerDamage+5;
             gameMaster.defense = gameMaster.defense+5;
             gameMaster.hp = gameMaster.hp+5;
             gameMaster.tableValues[index]= " ";
             gameMaster.tableValues[checkingIndex]="H";
             gameMaster.orbPower = 1;
             break;
         }
                  else{
             if(gameMaster.checkerForDamage==1){
                            if(gameMaster.upperDamage!=0){
                    gameMaster.upperDamage = gameMaster.lowerDamage+rand.nextInt(gameMaster.upperDamage-gameMaster.lowerDamage+1);
                }
                if(gameMaster.lowerDamage!=0){
                    gameMaster.lowerDamage = rand.nextInt(gameMaster.lowerDamage);            
                }
                if(gameMaster.defense!=0){
                    gameMaster.defense = rand.nextInt(gameMaster.defense);
                }
                
                if(gameMaster.hp!=0){
                gameMaster.hp = rand.nextInt(gameMaster.hp);
                }
            if(gameMaster.hp!=0){
            gameMaster.tableValues[index]= " ";
            gameMaster.tableValues[checkingIndex]="H"; 
            System.out.println("Day"+gameMaster.day+": You are in the Castle.\nEncounter!- Monster");
            gameMaster.orbPower = 0;
            break;
            }
            else{
            System.out.println("Sorry You are defeated by the Monster");
            System.out.println("you hp is zero");
        System.out.println("Do You want to play again or not.");
        System.out.println("1) play again");
        System.out.println("2) exit");
        
        int option6 = sc.nextInt();
        if(option6==1){
        extracted11();
        gameMaster.lowerDamage = 2;
        gameMaster.upperDamage = 4;        
        gameMaster.defense = 1;
        gameMaster.hp = 20;
        gameMaster.orbPower = 0;
        gameMaster.checker = 0;
        gameMaster.MonsterDamage = 15;
        gameMaster.day = 1;
            Action.townMenu(sc,rand);
        }
        else{
        System.out.println("Game Ended.");            
         System.exit(0);
        }
         
            }
            
            }
              else{
             gameMaster.tableValues[index]= " ";
            gameMaster.tableValues[checkingIndex]="H"; 
            System.out.println("Day"+gameMaster.day+": You are in the Castle.\nEncounter!- Monster");
            gameMaster.orbPower = 0;
            break;
             }
                        
         }
        }
        else{
           System.out.println("Sorry you cannot escape the Dungeon! "); 
           continue outer3;
        }
        
    }
    
        else if (move == 's') {
            if(index!=56 && index!=57 && index!=58 && index!=59 && index!=60 && index!=61 && index!=62 && index!=63){
            checkingIndex = index+8;
                if(gameMaster.tableValues[checkingIndex] == "T"){
                gameMaster.tableValues[checkingIndex]="H/T";
                gameMaster.tableValues[index] = "T";
                System.out.println("You are in the Dungeon! ");
                break;
                
            }
         else if(gameMaster.tableValues[checkingIndex]=="O"){             
             System.out.println("You found the Orb of Power! ");
             System.out.println("Your attack increases by 5! ");
             System.out.println("Your defence increases by 5!  ");
             System.out.println("Day"+gameMaster.day+": You are in the Castle.\nEncounter!- Monster");
             gameMaster.upperDamage = gameMaster.upperDamage+5;
             gameMaster.lowerDamage = gameMaster.lowerDamage+5;
             gameMaster.defense = gameMaster.defense+5;
             gameMaster.hp = gameMaster.hp+5;
             gameMaster.tableValues[index]= " ";
             gameMaster.tableValues[checkingIndex]="H";
             gameMaster.orbPower = 1;
             break;
         }
                  else{
             if(gameMaster.checkerForDamage==1){
                             if(gameMaster.upperDamage!=0){
                    gameMaster.upperDamage = gameMaster.lowerDamage+rand.nextInt(gameMaster.upperDamage-gameMaster.lowerDamage+1);
                }
                if(gameMaster.lowerDamage!=0){
                    gameMaster.lowerDamage = rand.nextInt(gameMaster.lowerDamage);            
                }
                if(gameMaster.defense!=0){
                    gameMaster.defense = rand.nextInt(gameMaster.defense);
                }
                
                if(gameMaster.hp!=0){
                gameMaster.hp = rand.nextInt(gameMaster.hp);
                }
            if(gameMaster.hp!=0){
            gameMaster.tableValues[index]= " ";
            gameMaster.tableValues[checkingIndex]="H"; 
            System.out.println("Day"+gameMaster.day+": You are in the Castle.\nEncounter!- Monster");
            gameMaster.orbPower = 0;
            break;
            }
            else{
            System.out.println("Sorry You are defeated by the Monster");
            System.out.println("you hp is zero");
        System.out.println("Do You want to play again or not.");
        System.out.println("1) play again");
        System.out.println("2) exit");
        
        int option7 = sc.nextInt();
        if(option7==1){
        gameMaster.name = "The Hero";
        gameMaster.lowerDamage = 2;
        gameMaster.upperDamage = 4;        
        gameMaster.defense = 1;
        gameMaster.hp = 20;
        gameMaster.orbPower = 0;
        gameMaster.checker = 0;
        gameMaster.MonsterDamage = 15;
        gameMaster.day = 1;
            Action.townMenu(sc,rand);
        }
        else{
        System.out.println("Game Ended.");            
         System.exit(0);
        }
         
            }
            
            }
              else{
            gameMaster.tableValues[index]= " ";
            gameMaster.tableValues[checkingIndex]="H"; 
            System.out.println("Day"+gameMaster.day+": You are in the Castle.\nEncounter!- Monster");
            gameMaster.orbPower = 0;
            break;
             }
                        
         }
        }
        else{
           System.out.println("Sorry you cannot escape the Dungeon! "); 
           continue outer3;
        }
        
        }
        
        }
        
    }
	private static String extracted11() {
		String string = extracted11();
		String string2 = string;
		String string1 = string2;
		return string1;
	}
}


