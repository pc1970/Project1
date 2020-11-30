package automationUITests;

import java.io.FileWriter;
import java.io.IOException;
import java.util.Random;
import java.util.Scanner;
import java.util.concurrent.TimeUnit;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

public class actionTest {
	WebDriver driver;
	static gameMasterTest gm=new gameMasterTest();
    public static dungeonTest d=new  dungeonTest();
//     public static Action a=new Action();
     
	
	@BeforeMethod
	public void setUp() {
		
		System.setProperty("webdriver.gecko.driver","C:\\SeleniumGecko\\geckodriver.exe");

		driver = new FirefoxDriver();
		driver.manage().timeouts().pageLoadTimeout(30, TimeUnit.SECONDS);
		driver.manage().timeouts().implicitlyWait(20, TimeUnit.SECONDS);
		driver.manage().window().maximize();
		driver.manage().deleteAllCookies();		
		
	}
	
	 @Test
	    public static void townMenuTest(Scanner sc,Random rand) {
		 outer2:
		        while(true){
		        System.out.println("NeverDodol's Menu"); 
		        System.out.println("Day"+gameMasterTest.day+": \nYou are in NeverDodol's Castle.");
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
		            dungeonTest.mapTest();
		            continue outer2;
		        }
		        else if(againOption==3){
		            //System.out.println("Before Updating Day : "+gm.day);
		        	gameMasterTest.day++;
		            //System.out.println("After Updating Day : "+gm.day);
		            System.out.println("Day"+gameMasterTest.day+": You are in the Castle.\nEncounter!- Monster");
		            gameMasterTest.checkerForDamage = 1;
		                                  
		               moveTest(sc,rand);                
		               gameMasterTest.combatMenuTest(sc,rand);
		                break;
		        }
		        else if(againOption==4){
		        	gameMasterTest.resetTest();
		        }
		        else if(againOption==5){
		            int index = 0;
		            for(int i=0;i<64;i++){
		                if(gameMasterTest.tableValues[i]=="H"){
		                    index=i;
		                }
		            }
		          
		          String str9 = Integer.toString(index)+"\n";
		         int dayInteger = gameMasterTest.day;
		        String str1 = Integer.toString(dayInteger)+"\n";
		        int hpInteger = gameMasterTest.hp;
		        String str2 = Integer.toString(hpInteger)+"\n";
		        int defenceInteger = gameMasterTest.defense;
		        String str3 = Integer.toString(defenceInteger)+"\n";
		        int lDamageInteger = gameMasterTest.lowerDamage;
		        String str4 = Integer.toString(lDamageInteger)+"\n";
		        int uDamageInteger = gameMasterTest.upperDamage;
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
		        gameMasterTest.name = "The Hero";
		        gameMasterTest.lowerDamage = 2;
		        gameMasterTest.upperDamage = 4;        
		        gameMasterTest.defense = 1;
		        gameMasterTest.hp = 20;
		        gameMasterTest.orbPower = 0;
		        gameMasterTest.checker =0;
		        gameMasterTest.MonsterDamage = 15;
		        gameMasterTest.day = 1;
		            townMenuTest(sc,rand);
		        }
		        else{
		        System.out.println("Game Ended.");            
		         System.exit(0);
		         break;
		        }
		                     
		        }
		        
		        }
	    }
	 
	 @Test
	    public static void attackTest(Random rand,Scanner sc) {
		 
		 if( gameMasterTest.upperDamage!=0){
			 gameMasterTest.upperDamage = gameMasterTest.lowerDamage+rand.nextInt(gameMasterTest.upperDamage-gameMasterTest.lowerDamage+1);
         }
         if(gameMasterTest.lowerDamage!=0){
        	 gameMasterTest.lowerDamage = rand.nextInt(gameMasterTest.lowerDamage);            
         }
         if(gameMasterTest.defense!=0){
        	 gameMasterTest.defense = rand.nextInt(gameMasterTest.defense);
         }
         
         int newhp = gameMasterTest.hp;
         if(gameMasterTest.hp!=0){
        	 gameMasterTest.hp = rand.nextInt(gameMasterTest.hp);
         }
         
         int finalhp= newhp-gameMasterTest.hp;
         if(gameMasterTest.MonsterDamage!=0){
        	 gameMasterTest.MonsterDamage = rand.nextInt(gameMasterTest.MonsterDamage);
         }
         
         if(gameMasterTest.orbPower!=1){
             System.out.println("You do not have the Orb of Power - the Monster is immune! ");
         }
         System.out.println("Player's HP: "+gameMasterTest.hp);
         System.out.println("MonsterDamage's HP: "+gameMasterTest.MonsterDamage);
         
         if(gameMasterTest.hp!=0){
          System.out.println("You deal "+finalhp+" damage to the Monster");
         System.out.println("Oouch the Monster hit you for "+gameMasterTest.MonsterDamage+" damage.\nEncounter!- Monster");
        
         if(gameMasterTest.orbPower==1 && gameMasterTest.MonsterDamage==0){
         System.out.println("You deal "+gameMasterTest.MonsterDamage+" damage to the Monster ");
         System.out.println("The Monster is dead! You are victorious! ");
         System.out.println("Congratulations, you have defeated the Dungeon Monster! ");
         System.out.println("The world is saved! You win!  ");
         System.out.println("You Won Fight in  "+gameMasterTest.day+" days");                
         }
         System.out.println("Demage: "+gameMasterTest.lowerDamage+" to "+gameMasterTest.upperDamage);
         System.out.println("Defence: "+gameMasterTest.defense);
         System.out.println("HP: "+gameMasterTest.hp);
           
         }
         
         else{                
         System.out.println("Do You want to play again or not.");
         System.out.println("1) play again");
         System.out.println("2) exit");
        
         int option3 = sc.nextInt();
         if(option3==1){
          gameMasterTest.name = "The Hero";
          gameMasterTest.lowerDamage = 2;
          gameMasterTest.upperDamage = 4;        
          gameMasterTest.defense = 1;
          gameMasterTest.hp = 20;
          gameMasterTest.orbPower = 0;
          gameMasterTest.checker =0;
          gameMasterTest.MonsterDamage = 15;
          gameMasterTest.day = 1;
           actionTest.townMenuTest(sc,rand);
         }
         else{
         System.out.println("Game Ended.");            
          System.exit(0);
         }
         
         }
		 
	    }
	 
	 @Test
	    public static void moveTest(Scanner sc,Random rand) {
		 
		 outer3:
		        while(true){
		        int index = 0;
		        int checkingIndex = 0;
		        System.out.println("W = up; A = left; S = down; D = right ");
		        char move = sc.next().charAt(0);
		        System.out.println("Your Move:");        
		        System.out.println(move);
		        
		        for(int i=0;i<64;i++){
		                if(gameMasterTest.tableValues[i]=="H" || gameMasterTest.tableValues[i]=="H/T"){
		                    index = i;
		                    break;
		                }
		         }

		          
		        if (move == 'a') {            
		            if(index!=0){
		            checkingIndex = index-1;
		            
		            if(gameMasterTest.tableValues[checkingIndex] == "T"){
		            	gameMasterTest.tableValues[checkingIndex]="H/T";
		                gameMasterTest.tableValues[index] = "T";
		                System.out.println("You are in the Dungeon! ");
		                break;
		            }
		            
		         else if(gameMasterTest.tableValues[checkingIndex]=="O"){             
		             System.out.println("You found the Orb of Power! ");
		             System.out.println("Your attack increases by 5! ");
		             System.out.println("Your defence increases by 5!  ");
		             System.out.println("Day"+gameMasterTest.day+": You are in the Castle.\nEncounter!- Monster");
		             gameMasterTest.upperDamage = gameMasterTest.upperDamage+5;
		             gameMasterTest.lowerDamage = gameMasterTest.lowerDamage+5;
		             gameMasterTest.defense = gameMasterTest.defense+5;
		             gameMasterTest.hp = gameMasterTest.hp+5;
		             gameMasterTest.tableValues[checkingIndex]="H";
		             gameMasterTest.tableValues[index]= " ";
		             gameMasterTest.orbPower = 1;
		             break;
		         }
		         else{
		             if(gameMasterTest.checkerForDamage==1){
		                 if(gameMasterTest.upperDamage!=0){
		                	 gameMasterTest.upperDamage = gameMasterTest.lowerDamage+rand.nextInt(gameMasterTest.upperDamage-gameMasterTest.lowerDamage+1);
		                }
		                if(gameMasterTest.lowerDamage!=0){
		                	gameMasterTest.lowerDamage = rand.nextInt(gameMasterTest.lowerDamage);            
		                }
		                if(gameMasterTest.defense!=0){
		                	gameMasterTest.defense = rand.nextInt(gameMasterTest.defense);
		                }
		                
		                if(gameMasterTest.hp!=0){
		                	gameMasterTest.hp = rand.nextInt(gameMasterTest.hp);
		                }
		                
		            if(gameMasterTest.hp!=0){
		            	gameMasterTest.tableValues[index]= " ";
		            	gameMasterTest.tableValues[checkingIndex]="H"; 
		            System.out.println("Day"+gameMasterTest.day+": You are in the Castle.\nEncounter!- Monster");
		            gameMasterTest.orbPower = 0;
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
		                	gameMasterTest.name = "The Hero";
		                	gameMasterTest.lowerDamage = 2;
		                	gameMasterTest.upperDamage = 4;        
		                	gameMasterTest.defense = 1;
		                	gameMasterTest.hp = 20;
		                	gameMasterTest.orbPower = 0;
		                	gameMasterTest.checker =0;
		                	gameMasterTest.MonsterDamage = 15;
		                	gameMasterTest.day = 1;
		                	actionTest.townMenuTest(sc,rand);
		                }
		                else{
		                System.out.println("Game Ended.");            
		                 System.exit(0);
		                }
		            }
		            
		            }
		            
		              else{
		            	  gameMasterTest.tableValues[index]= " ";
		            	  gameMasterTest.tableValues[checkingIndex]="H";             
		            System.out.println("Day"+gameMasterTest.day+": You are in the Castle.\nEncounter!- Monster");
		            gameMasterTest.orbPower = 0;
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
		                  if(gameMasterTest.tableValues[checkingIndex] == "T"){
		                	  gameMasterTest.tableValues[checkingIndex]="H/T";
		                gameMasterTest.tableValues[index] = "T";
		                System.out.println("You are in the Dungeon! ");
		                break;
		            }
		         else if(gameMasterTest.tableValues[checkingIndex]=="O"){             
		             System.out.println("You found the Orb of Power! ");
		             System.out.println("Your attack increases by 5! ");
		             System.out.println("Your defence increases by 5!  ");
		             System.out.println("Day"+gameMasterTest.day+": You are in the Castle.\nEncounter!- Monster");
		             gameMasterTest.upperDamage = gameMasterTest.upperDamage+5;
		             gameMasterTest.lowerDamage = gameMasterTest.lowerDamage+5;
		             gameMasterTest.defense = gameMasterTest.defense+5;
		             gameMasterTest.hp = gameMasterTest.hp+5;
		             gameMasterTest.tableValues[index]= " ";
		             gameMasterTest.tableValues[checkingIndex]="H";
		             gameMasterTest.orbPower = 1;
		             break;
		         }
		                  else{
		             if(gameMasterTest.checkerForDamage==1){
		                            if(gameMasterTest.upperDamage!=0){
		                            	gameMasterTest.upperDamage = gameMasterTest.lowerDamage+rand.nextInt(gameMasterTest.upperDamage-gameMasterTest.lowerDamage+1);
		                }
		                if(gameMasterTest.lowerDamage!=0){
		                	gameMasterTest.lowerDamage = rand.nextInt(gameMasterTest.lowerDamage);            
		                }
		                if(gameMasterTest.defense!=0){
		                	gameMasterTest.defense = rand.nextInt(gameMasterTest.defense);
		                }
		                
		                if(gameMasterTest.hp!=0){
		                	gameMasterTest.hp = rand.nextInt(gameMasterTest.hp);
		                }
		            if(gameMasterTest.hp!=0){
		            	gameMasterTest.tableValues[index]= " ";
		            	gameMasterTest.tableValues[checkingIndex]="H"; 
		            System.out.println("Day"+gameMasterTest.day+": You are in the Castle.\nEncounter!- Monster");
		            gameMasterTest.orbPower = 0;
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
		        	gameMasterTest.name = "The Hero";
		        gameMasterTest.lowerDamage = 2;
		        gameMasterTest.upperDamage = 4;        
		        gameMasterTest.defense = 1;
		        gameMasterTest.hp = 20;
		        gameMasterTest.orbPower = 0;
		        gameMasterTest.checker =0;
		        gameMasterTest.MonsterDamage = 15;
		        gameMasterTest.day = 1;
		        actionTest.townMenuTest(sc,rand);
		        }
		        else{
		        System.out.println("Game Ended.");            
		         System.exit(0);
		        }
		         
		            
		            }
		            
		            }
		              else{
		            	  gameMasterTest.tableValues[index]= " ";
		             gameMasterTest.tableValues[checkingIndex]="H"; 
		            System.out.println("Day"+gameMasterTest.day+": You are in the Castle.\nEncounter!- Monster");
		            gameMasterTest.orbPower = 0;
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
		               if(gameMasterTest.tableValues[checkingIndex] == "T"){
		            	   gameMasterTest.tableValues[checkingIndex]="H/T";
		                gameMasterTest.tableValues[index] = "T";
		                System.out.println("You are in the Dungeon! ");
		                break;
		            }
		         else if(gameMasterTest.tableValues[checkingIndex]=="O"){             
		             System.out.println("You found the Orb of Power! ");
		             System.out.println("Your attack increases by 5! ");
		             System.out.println("Your defence increases by 5!  ");
		             System.out.println("Day"+gameMasterTest.day+": You are in the Castle.\nEncounter!- Monster");
		             gameMasterTest.upperDamage = gameMasterTest.upperDamage+5;
		             gameMasterTest.lowerDamage = gameMasterTest.lowerDamage+5;
		             gameMasterTest.defense = gameMasterTest.defense+5;
		             gameMasterTest.hp = gameMasterTest.hp+5;
		             gameMasterTest.tableValues[index]= " ";
		             gameMasterTest.tableValues[checkingIndex]="H";
		             gameMasterTest.orbPower = 1;
		             break;
		         }
		                  else{
		             if(gameMasterTest.checkerForDamage==1){
		                            if(gameMasterTest.upperDamage!=0){
		                            	gameMasterTest.upperDamage = gameMasterTest.lowerDamage+rand.nextInt(gameMasterTest.upperDamage-gameMasterTest.lowerDamage+1);
		                }
		                if(gameMasterTest.lowerDamage!=0){
		                	gameMasterTest.lowerDamage = rand.nextInt(gameMasterTest.lowerDamage);            
		                }
		                if(gameMasterTest.defense!=0){
		                	gameMasterTest.defense = rand.nextInt(gameMasterTest.defense);
		                }
		                
		                if(gameMasterTest.hp!=0){
		                	gameMasterTest.hp = rand.nextInt(gameMasterTest.hp);
		                }
		            if(gameMasterTest.hp!=0){
		            	gameMasterTest.tableValues[index]= " ";
		            	gameMasterTest.tableValues[checkingIndex]="H"; 
		            System.out.println("Day"+gameMasterTest.day+": You are in the Castle.\nEncounter!- Monster");
		            gameMasterTest.orbPower = 0;
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
		        	gameMasterTest.name = "The Hero";
		        gameMasterTest.lowerDamage = 2;
		        gameMasterTest.upperDamage = 4;        
		        gameMasterTest.defense = 1;
		        gameMasterTest.hp = 20;
		        gameMasterTest.orbPower = 0;
		        gameMasterTest.checker =0;
		        gameMasterTest.MonsterDamage = 15;
		        gameMasterTest.day = 1;
		        actionTest.townMenuTest(sc,rand);
		        }
		        else{
		        System.out.println("Game Ended.");            
		         System.exit(0);
		        }
		         
		            }
		            
		            }
		              else{
		            	  gameMasterTest.tableValues[index]= " ";
		            	  gameMasterTest.tableValues[checkingIndex]="H"; 
		            System.out.println("Day"+gameMasterTest.day+": You are in the Castle.\nEncounter!- Monster");
		            gameMasterTest.orbPower = 0;
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
		                if(gameMasterTest.tableValues[checkingIndex] == "T"){
		                	gameMasterTest.tableValues[checkingIndex]="H/T";
		                gameMasterTest.tableValues[index] = "T";
		                System.out.println("You are in the Dungeon! ");
		                break;
		                
		            }
		         else if(gameMasterTest.tableValues[checkingIndex]=="O"){             
		             System.out.println("You found the Orb of Power! ");
		             System.out.println("Your attack increases by 5! ");
		             System.out.println("Your defence increases by 5!  ");
		             System.out.println("Day"+gameMasterTest.day+": You are in the Castle.\nEncounter!- Monster");
		             gameMasterTest.upperDamage = gameMasterTest.upperDamage+5;
		             gameMasterTest.lowerDamage = gameMasterTest.lowerDamage+5;
		             gameMasterTest.defense = gameMasterTest.defense+5;
		             gameMasterTest.hp = gameMasterTest.hp+5;
		             gameMasterTest.tableValues[index]= " ";
		             gameMasterTest.tableValues[checkingIndex]="H";
		             gameMasterTest.orbPower = 1;
		             break;
		         }
		                  else{
		             if(gameMasterTest.checkerForDamage==1){
		                             if(gameMasterTest.upperDamage!=0){
		                            	 gameMasterTest.upperDamage = gameMasterTest.lowerDamage+rand.nextInt(gameMasterTest.upperDamage-gameMasterTest.lowerDamage+1);
		                }
		                if(gameMasterTest.lowerDamage!=0){
		                	gameMasterTest.lowerDamage = rand.nextInt(gameMasterTest.lowerDamage);            
		                }
		                if(gameMasterTest.defense!=0){
		                	gameMasterTest.defense = rand.nextInt(gameMasterTest.defense);
		                }
		                
		                if(gameMasterTest.hp!=0){
		                	gameMasterTest.hp = rand.nextInt(gameMasterTest.hp);
		                }
		            if(gameMasterTest.hp!=0){
		            	gameMasterTest.tableValues[index]= " ";
		            gameMasterTest.tableValues[checkingIndex]="H"; 
		            System.out.println("Day"+gameMasterTest.day+": You are in the Castle.\nEncounter!- Monster");
		            gameMasterTest.orbPower = 0;
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
		        	gameMasterTest.name = "The Hero";
		        	gameMasterTest.lowerDamage = 2;
		        	gameMasterTest.upperDamage = 4;        
		        	gameMasterTest.defense = 1;
		        	gameMasterTest.hp = 20;
		        	gameMasterTest.orbPower = 0;
		        	gameMasterTest.checker =0;
		        	gameMasterTest.MonsterDamage = 15;
		        	gameMasterTest.day = 1;
		            actionTest.townMenuTest(sc,rand);
		        }
		        else{
		        System.out.println("Game Ended.");            
		         System.exit(0);
		        }
		         
		            }
		            
		            }
		              else{
		            	  gameMasterTest.tableValues[index]= " ";
		            gameMasterTest.tableValues[checkingIndex]="H"; 
		            System.out.println("Day"+gameMasterTest.day+": You are in the Castle.\nEncounter!- Monster");
		            gameMasterTest.orbPower = 0;
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
		 
	   			
		@AfterMethod
		public void tearDown() {
			driver.quit();
			
		}

}
