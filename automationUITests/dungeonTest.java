package automationUITests;

import java.util.concurrent.TimeUnit;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

public class dungeonTest {
	WebDriver driver;
    static gameMasterTest gm=new gameMasterTest();

	
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
	public static void mapTest() {
		
		System.out.println("+---+---+---+---+---+---+---+---+ ");
        System.out.println("| "+gameMasterTest.tableValues[0]+" | "+gameMasterTest.tableValues[1]+" | "+gameMasterTest.tableValues[2]+" | "+gameMasterTest.tableValues[3]+" | "
        +gameMasterTest.tableValues[4]+" | "+gameMasterTest.tableValues[5]+" | "+gameMasterTest.tableValues[6]+" | "+gameMasterTest.tableValues[7]+" | ");
        System.out.println("+---+---+---+---+---+---+---+---+ ");
        System.out.println("| "+gameMasterTest.tableValues[8]+" | "+gameMasterTest.tableValues[9]+" | "+gameMasterTest.tableValues[10]+" | "+gameMasterTest.tableValues[11]+" | "
        +gameMasterTest.tableValues[12]+" | "+gameMasterTest.tableValues[13]+" | "+gameMasterTest.tableValues[14]+" | "+gameMasterTest.tableValues[15]+" | ");
        System.out.println("+---+---+---+---+---+---+---+---+ ");
        System.out.println("| "+gameMasterTest.tableValues[16]+" | "+gameMasterTest.tableValues[17]+" | "+gameMasterTest.tableValues[18]+" | "+gameMasterTest.tableValues[19]+" | "
        +gameMasterTest.tableValues[20]+" | "+gameMasterTest.tableValues[21]+" | "+gameMasterTest.tableValues[22]+" | "+gameMasterTest.tableValues[23]+" | ");
        System.out.println("+---+---+---+---+---+---+---+---+ ");
        System.out.println("| "+gameMasterTest.tableValues[24]+" | "+gameMasterTest.tableValues[25]+" | "+gameMasterTest.tableValues[26]+" | "+gameMasterTest.tableValues[27]+" | "
        +gameMasterTest.tableValues[28]+" | "+gameMasterTest.tableValues[29]+" | "+gameMasterTest.tableValues[30]+" | "+gameMasterTest.tableValues[31]+" | ");
        System.out.println("+---+---+---+---+---+---+---+---+ ");
        System.out.println("| "+gameMasterTest.tableValues[32]+" | "+gameMasterTest.tableValues[33]+" | "+gameMasterTest.tableValues[34]+" | "+gameMasterTest.tableValues[35]+" | "
        +gameMasterTest.tableValues[36]+" | "+gameMasterTest.tableValues[37]+" | "+gameMasterTest.tableValues[38]+" | "+gameMasterTest.tableValues[39]+" | ");
        System.out.println("+---+---+---+---+---+---+---+---+ ");
        System.out.println("| "+gameMasterTest.tableValues[40]+" | "+gameMasterTest.tableValues[41]+" | "+gameMasterTest.tableValues[42]+" | "+gameMasterTest.tableValues[43]+" | "
        +gameMasterTest.tableValues[44]+" | "+gameMasterTest.tableValues[45]+" | "+gameMasterTest.tableValues[46]+" | "+gameMasterTest.tableValues[47]+" | ");
        System.out.println("+---+---+---+---+---+---+---+---+ ");
        System.out.println("| "+gameMasterTest.tableValues[48]+" | "+gameMasterTest.tableValues[49]+" | "+gameMasterTest.tableValues[50]+" | "+gameMasterTest.tableValues[51]+" | "
        +gameMasterTest.tableValues[52]+" | "+gameMasterTest.tableValues[53]+" | "+gameMasterTest.tableValues[54]+" | "+gameMasterTest.tableValues[55]+" | ");
        System.out.println("+---+---+---+---+---+---+---+---+ ");
        System.out.println("| "+gameMasterTest.tableValues[56]+" | "+gameMasterTest.tableValues[57]+" | "+gameMasterTest.tableValues[58]+" | "+gameMasterTest.tableValues[59]+" | "
        +gameMasterTest.tableValues[60]+" | "+gameMasterTest.tableValues[61]+" | "+gameMasterTest.tableValues[62]+" | "+gameMasterTest.tableValues[63]+" | ");

		
		}
	
	
	@AfterMethod
	public void tearDown() {
		driver.quit();
		
	}
		
	

}
