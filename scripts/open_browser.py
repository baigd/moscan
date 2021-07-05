import mydriver
from selenium.webdriver.common.by import By
import time

# start browser
driver2 = mydriver.efficientChrome(False, "chrome-profile2", "127.0.0.1:8081")
driver = mydriver.efficientChrome(False, "chrome-profile5", "127.0.0.1:8080")

# website = "https://ask.fm/login"
website = "https://thetakeout.com"
driver2.get(website)
driver.get(website)
