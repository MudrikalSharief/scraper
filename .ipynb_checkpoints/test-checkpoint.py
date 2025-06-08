#%%
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import time
import os
#%%
load_dotenv()
# Get credentials from environment variables
username = os.environ.get('Email')
password = os.environ.get('Password')

driver = webdriver.Chrome()
driver.get("https://www.linkedin.com/login")
assert "LinkedIn" in driver.title

# Find the Username 
elem = driver.find_element(By.ID, "username")
# Add a delay of 2 seconds before entering email
time.sleep(2)
# Clear the input
elem.clear()

# Type the Username
elem.send_keys(username)

# Add a delay of 1 seconds before entering password
time.sleep(1)

# Find the Password
p_word = driver.find_element(By.ID, "password")
# Clear the input
p_word.clear()
p_word.send_keys(password)
# Press Login

# Use CSS selector for multiple classes
login_button = driver.find_element(By.CSS_SELECTOR, "button.btn__primary--large.from__button--floating")

# Add a delay of 1 seconds before entering password
time.sleep(1)

# Then click the button
login_button.click()




assert "No results found." not in driver.page_source
input("Press Enter to close the browser...")
driver.close()