package automationUITests;

import java.util.concurrent.TimeUnit;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

public class heroTest {
	WebDriver driver;
	 static gameMasterTest gm=new gameMasterTest();
	    roomTest r1=new roomTest();
	
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
	    public void actionMethodTest() {
		 gameMasterTest.name = "The Hero";
		 gameMasterTest.lowerDamage = 2;
		 gameMasterTest.upperDamage = 4;        
		 gameMasterTest.defense = 1;
		 gameMasterTest.hp = 20;
		 gameMasterTest.orbPower = 0;
		 gameMasterTest.checker =0;
		 gameMasterTest.MonsterDamage = 15;
		 gameMasterTest.day = 1;
         roomTest.characteristicsTest();
	    }
			
			
		@AfterMethod
		public void tearDown() {
			driver.quit();
			
		}

}
