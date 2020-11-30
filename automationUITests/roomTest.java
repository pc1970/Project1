package automationUITests;

import java.util.concurrent.TimeUnit;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

public class roomTest {
	
	WebDriver driver;
	 static gameMasterTest gm=new gameMasterTest();
//	    roomTest r1=new roomTest();
	
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
	    public static void characteristicsTest() {
		 
		 System.out.println("Player Characteristics are:");
	        System.out.println("Name: "+gameMasterTest.name);
	        System.out.println("Demage: "+gameMasterTest.lowerDamage+" to "+gameMasterTest.upperDamage);
	        System.out.println("Defence: "+gameMasterTest.defense);
	        System.out.println("HP: "+gameMasterTest.hp);
		 
	    }
			
			
		@AfterMethod
		public void tearDown() {
			driver.quit();
			
		}

}
