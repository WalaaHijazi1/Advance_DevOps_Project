from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os



driver_options = Options()

driver_options.add_argument("--headless=new")
driver_options.add_argument("--no-sandbox")
driver_options.add_argument("--disable-dev-shm-usage")


driver_options.add_argument(f"--user-data-dir={os.path.expanduser('~')}/chrome_data")

driver_options.add_argument("--remote-debugging-port=9222")  # Unique devtools port

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=driver_options)



try:
    # Navigate to Google
    driver.get("https://www.google.com")

    # Verify the page title
    assert "Google" in driver.title
    print("Page title is correct.")

    # Take a screenshot
    driver.save_screenshot("screenshot.png")
    print("Screenshot saved as 'screenshot.png'.")

finally:
    # Close the browser
    driver.quit()

