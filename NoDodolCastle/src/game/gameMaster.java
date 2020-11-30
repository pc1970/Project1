package game;

import java.util.*;
import java.awt.event.KeyEvent;
import java.awt.event.KeyAdapter;
import java.util.Random;
import java.lang.*;
import java.io.File;  
import java.io.IOException;  
import java.util.Scanner; 
import java.io.FileWriter;  
import java.io.FileNotFoundException;
import java.util.HashMap;

@SuppressWarnings("unused")
public class gameMaster extends KeyAdapter
{   
    public static String name;
    public static int lowerDamage;
    public static int upperDamage;
    public static int defense;
    public static int hp;
    public static int checker;
    public static int day;
    public static int MonsterDamage;
    public static int orbPower;
    public static int checkerForDamage = 1;
    public static String[] tableValues = new String[64];
    public static Dungeon d=new  Dungeon();
    public static Action a=new Action();
    public static Multiplayer h;
   
   public static  HashMap<String, Multiplayer> players = new HashMap<String, Multiplayer>();
   public static  HashMap<String, Weapon> weapons = new HashMap<String, Weapon>();
   public static  HashMap<String, Monster> monsters = new HashMap<String, Monster>();
   
     public gameMaster()
    {
                
    }
       public static void main(String[] args) {
        
        day = 1;
        orbPower = 0;
        checker = 0;
        MonsterDamage = 15;        
        Scanner sc= new Scanner(System.in);
        Random rand = new Random();                                             
        
        for(int i=0;i<64;i++){
            tableValues[i] = " ";
        }
        
            for(int i=0;i<64;i++){
                if(i>=2 && i<60 && tableValues[i]==" "){
                    int j=2+rand.nextInt(60-2+1);
                    tableValues[j]="O";
                }
            }

        Monster[] m = new Monster[3];
        m[0] = new Monster( "Devil" , 1900 );
        m[1] = new Monster( "Deamon", 1300 );
        m[2] = new Monster( "Bad"   , 1200 );

        for ( int i = 0; i < 3; i++ ) {
            monsters.put( m[i].getName(), m[i] );
        }

        Weapon[] w = new Weapon[3];
        w[0] = new Weapon( "Sword", 100  );
        w[1] = new Weapon( "Bomb" , 1000 );
        w[2] = new Weapon( "Bat"  , 500  );

        for ( int i = 0; i < 3; i++ ) {
            weapons.put( w[i].getName(), w[i] );
        }

        //  new Weapon().setUpWeapons(weapons); //Setting up Weapons for the Game
        //  new Monster().setUpMonsters(monsters); //Setting up Monsters for the Game

        while(true){
        System.out.println("Enter User Name('exit' to exit):");
        String un = sc.nextLine();
        if(un.equals("exit")){
           // System.out.println(un);
            break;}
        
        if(players.containsKey(un)){
              System.out.println("User Already Exists!");
              System.out.println("Loading Profile......");
             h = players.get(un);
             printProfile(h);
        }
        else{
         h = new Multiplayer(un);
         players.put(un,h);
        }
        
        System.out.println("Welcome to Dodolventure");
        System.out.println("----------------------------------");
        System.out.println("Main Menu");               
        System.out.println("1) New Game");
        System.out.println("2) Resume Game");
        System.out.println("3) Reset Game");
        System.out.println("4) Save Game");
        System.out.println("5) Exit Game");
        System.out.println("Enter choice.");              
        
        int option = sc.nextInt();
        if(option==1){            
       
           h.ActionMethod();
           
           // characteristics();
            tableValues[0] = "T";
            tableValues[11] = "T";
            tableValues[21] = "T";
            tableValues[25] = "T";
            tableValues[52] = "T";
            tableValues[63] = "K";
                   
            System.out.println("\nThe Default Map is:");
            Dungeon.map();
            Action.townMenu(sc,rand);
            
       }
       else if(option==2){
         String string = extracted1(name);
       int myIndex = 0; 
       int dataInteger = 0;
       int runners = 0;
      try {
      File myObj = new File("data.txt");
      Scanner myReader = new Scanner(myObj);
      while (myReader.hasNextLine()) {
        String data = myReader.nextLine();
        if(runners==0){
            myIndex = Integer.parseInt(data);
        }
        else if(runners==1){
            dataInteger = Integer.parseInt(data);
            day = dataInteger;
        }
        else if(runners==2){
            dataInteger = Integer.parseInt(data);
            hp = dataInteger;
        }
         else if(runners==3){
            dataInteger = Integer.parseInt(data);
            defense = dataInteger;
        }
         else if(runners==4){
            dataInteger = Integer.parseInt(data);
            lowerDamage = dataInteger;
        }
         else if(runners==5){
            dataInteger = Integer.parseInt(data);
            upperDamage = dataInteger;
        }
        runners++;       
      }
      myReader.close();
    } catch (FileNotFoundException e) {
      System.out.println("An error occurred.");
      e.printStackTrace();
    }  
           
           //characteristics();
            tableValues[0] = "T";
            tableValues[11] = "T";
            tableValues[21] = "T";
            tableValues[25] = "T";
            tableValues[52] = "T";
            tableValues[63] = "K";
            if(myIndex>0){
                if(myIndex==11 || myIndex==21 || myIndex==25 || myIndex==52 || myIndex==63){
                    tableValues[myIndex] = "H/T";
                }
                else{
                     tableValues[myIndex] = "H";
                }
                
                tableValues[0] = " ";
            }            
           /* System.out.println("\nThe Default Map is:");
            map();*/  
            System.out.println("\nThe Default Map is:");
            Dungeon d=new Dungeon();
            Dungeon.map();
            
            Action.townMenu(sc,rand);

       }
       else if(option == 3){
              h.ActionMethod();
           
           // characteristics();
            tableValues[0] = "T";
            tableValues[11] = "T";
            tableValues[21] = "T";
            tableValues[25] = "T";
            tableValues[52] = "T";
            tableValues[63] = "K";
       
            
            System.out.println("\nThe Default Map is:");
            Dungeon.map();
            Action.townMenu(sc,rand);
       }
       else if(option==4){           
        System.out.println("Do You want to play again or not.");
        System.out.println("1) play again");
        System.out.println("2) exit");
        
        int option1 = sc.nextInt();
        if(option1==1){
        extracted1(name);
        lowerDamage = 2;
        upperDamage = 4;        
        defense = 1;
        hp = 20;
        orbPower = 0;
        checker = 0;
        MonsterDamage = 15;
        day = 1;
            Action.townMenu(sc,rand);
        }
        else if(option == 5){
        System.out.println("Game Ended.");            
         System.exit(0);
        }
            
        }            
}
      }
	private static String extracted1(String name) {
		return name = gameMaster.name;
	}
	private static String extracted() {
		return extracted1(name);
	}   
    
    public static void outDoorMenu(Scanner sc,Random rand, String name){
                
                reset();
                outer:
                while(true){
                System.out.println("You run and Hide.");
                System.out.println("Outdoor Menu");
                System.out.println("1) View character.");
                System.out.println("2) View map.");
                System.out.println("3) Move.");
                System.out.println("4) Sense Orb.");
                System.out.println("5) Exit Game.");
                System.out.println("Enter choice.");
                int outdoorOption = sc.nextInt();
                if(outdoorOption==1){
                   //characteristics();
                    combatMenu(sc,rand);
                    break;
                }
                else if(outdoorOption==2){
                    Dungeon.map();
                    combatMenu(sc,rand);
                    break;
                }
                else if(outdoorOption==3){
                    day++;
                    checkerForDamage = 0;
                    Action.move(sc,rand);
                    if(orbPower==1){
                        combatMenu(sc,rand);
                        break;
                    }
                    continue outer;
                }
                else if(outdoorOption==4){
                    day++;
                    
                    for(int i=3;i<50;i++){                        
                        if(tableValues[i]=="O"){
                            if(i==3 || i==11 || i==19 || i==27 || i==35 || i==43 || i==51 ||  i==59){
                                System.out.println("You sense that the Orb of Power is to the North. ");
                                break;
                            }
                            else if(i>11 || i>19 || i>27 || i>35 || i>43 || i>51 ||  i>59){
                                System.out.println("You sense that the Orb of Power is to the Northwest. ");
                                break;
                            }
                            else if(i==10 || i==18 || i==26 || i==34 || i==42 || i==50 ||  i==58){
                                System.out.println("You sense that the Orb of Power is to the West. ");
                                break;
                            }
                            else{
                                System.out.println("You sense that the Orb of Power is to the Southeast. ");
                                break;
                            }
                                
                        }
                        
                    }
                    combatMenu(sc,rand);
                    break;
                }
                
                else {              
                             System.out.println("Do You want to play again or not.");
        System.out.println("1) play again");
        System.out.println("2) exit");
        
        int option8 = sc.nextInt();
        if(option8==1){
        name = gameMaster.name;
        lowerDamage = 2;
        upperDamage = 4;        
        defense = 1;
        hp = 20;
        orbPower = 0;
        checker = 0;
        MonsterDamage = 15;
        day = 1;
            Action.townMenu(sc,rand);
        }
        else{
        System.out.println("Game Ended.");            
         System.exit(0);
         break;
        }
                             
                }
                
                }
                
    
    }
    
    
    public static void reset(){
         hp = 20;
         day++;
         MonsterDamage = 15;
         System.out.println("You and the Monster are fully healed");
    }
    
    
    
    public static void combatMenu(Scanner sc,Random rand){
        System.out.println("Demage: "+lowerDamage+" to "+upperDamage);
       System.out.println("Defence: "+defense);
       System.out.println("HP: "+hp);
        outer1:
        while(true){                             
              System.out.println("Combat Menu");
             System.out.println("1) Attack.");
             System.out.println("2) Run.");
            System.out.println("Enter choice.");
            int combatOption = sc.nextInt();
            if(combatOption==1){               
                Action.attack(rand,sc);
                continue outer1;
            }
            else{                                
                outDoorMenu(sc,rand, name);
                break;
            }
        }
               
    
    }
    public static void printProfile(Multiplayer p){
    gameMaster h = p.gm;
    System.out.println("User Name: " + gameMaster.name);
    System.out.println("Lower Damage: "+ gameMaster.lowerDamage);
    System.out.println("Upper Damage: "+ gameMaster.upperDamage);
    System.out.println("Defense: "+ gameMaster.defense);
    System.out.println("hp : "+ gameMaster.hp);
    System.out.println("Checker: "+ gameMaster.checker);
    System.out.println("day : "+ gameMaster.day);
    System.out.println("Monster Damage: "+ gameMaster.MonsterDamage);
    System.out.println("Orb Power: "+ gameMaster.orbPower);
    System.out.println("Checker For Damage : "+ gameMaster.checkerForDamage);
    }
}
    
