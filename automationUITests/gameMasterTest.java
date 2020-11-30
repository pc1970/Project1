package automationUITests;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Random;
import java.util.Scanner;
import java.util.concurrent.TimeUnit;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

public class gameMasterTest {
	WebDriver driver;
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
	    public static dungeonTest d=new  dungeonTest();
	   public static actionTest a=new actionTest();
	
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
		public void mainTest() {
			
		 day = 1;
	        orbPower = 0;
	        checker =0;
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
	        
	          
	        System.out.println("Welcome to NeverDodolventure");
	        System.out.println("----------------------------------");
	        System.out.println("Main Menu");               
	        System.out.println("1) New Game");
	        System.out.println("2) Resume Game");
	        System.out.println("3) Exit Game");
	        System.out.println("Enter choice.");              
	        
	        int option = sc.nextInt();
	        if(option==1){            
	           /* name = "The Hero";
	            lowerDamage = 2;
	            upperDamage = 4;        
	            Defense = 1;
	            Hp = 20;
	            orbPower = 0;
	            checker =0;
	            MonsterDamage = 15;
	            day = 1;*/
	           heroTest h=new heroTest();
	           h.actionMethodTest();
	           
	           // characteristics();
	            tableValues[0] = "T";
	            tableValues[11] = "T";
	            tableValues[21] = "T";
	            tableValues[25] = "T";
	            tableValues[52] = "T";
	            tableValues[63] = "K";
	           /* System.out.println("\nThe Default Map is:");
	            map();  */
	            
	            System.out.println("\nThe Default Map is:");
	            dungeonTest.mapTest();
	            actionTest.townMenuTest(sc,rand);
	            
	       }
	       else if(option==2){
	         name = "The Hero";
	       int myIndex =0; 
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
	            dungeonTest d=new dungeonTest();
	            dungeonTest.mapTest();
	            
	            actionTest.townMenuTest(sc,rand);

	       }
	       else if(option==3){           
	        System.out.println("Do You want to play again or not.");
	        System.out.println("1) play again");
	        System.out.println("2) exit");
	        
	        int option1 = sc.nextInt();
	        if(option1==1){
	        name = "The Hero";
	        lowerDamage = 2;
	        upperDamage = 4;        
	        defense = 1;
	        hp = 20;
	        orbPower = 0;
	        checker =0;
	        MonsterDamage = 15;
	        day = 1;
	        actionTest.townMenuTest(sc,rand);
	        }
	        else{
	        System.out.println("Game Ended.");            
	         System.exit(0);
	        }
	            
	        }            
	}
  
    
    
    @Test
    public static void outDoorMenuTest(Scanner sc,Random rand) {
    	 resetTest();
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
             combatMenuTest(sc,rand);
             break;
         }
         else if(outdoorOption==2){
             dungeonTest.mapTest();
             combatMenuTest(sc,rand);
             break;
         }
         else if(outdoorOption==3){
             day++;
             checkerForDamage = 0;
             actionTest.moveTest(sc,rand);
             if(orbPower==1){
            	 combatMenuTest(sc,rand);
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
             combatMenuTest(sc,rand);
             break;
         }
         
         else {              
                      System.out.println("Do You want to play again or not.");
                      System.out.println("1) play again");
                      System.out.println("2) exit");
 
                      int option8 = sc.nextInt();
                      if(option8==1){
                    	  name = "The Hero";
                    	  lowerDamage = 2;
                    	  upperDamage = 4;        
                    	  defense = 1;
                    	  hp = 20;
                    	  orbPower = 0;
                    	  checker =0;
                    	  MonsterDamage = 15;
                    	  day = 1;
                    	  actionTest.townMenuTest(sc,rand);
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
    public static void resetTest() {
    	 hp = 20;
         day++;
         MonsterDamage = 15;
         System.out.println("You and the Monster are fully healed");
    }
    
    
    @Test
    public static void combatMenuTest(Scanner sc, Random rand) {
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
                  actionTest.attackTest(rand,sc);
                  continue outer1;
              }
              else{                                
                  outDoorMenuTest(sc,rand);
                  break;
              }
          }
                 
      
      }
    		
	@AfterMethod
	public void tearDown() {
		driver.quit();
		
	}
		
	

}
