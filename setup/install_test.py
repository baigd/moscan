from selenium.webdriver.chrome.options import Options
from selenium import webdriver

chrome_options = Options()
chrome_options.add_argument('--proxy-server=' + "127.0.0.1:8080")
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get("https://google.com")