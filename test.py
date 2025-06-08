#%%
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time
import os


load_dotenv()
# Get credentials from environment variables
username = os.environ.get('Email')
password = os.environ.get('Password')
#====================================================================
#%%
driver = webdriver.Chrome()
driver.get("https://www.linkedin.com/login")
assert "LinkedIn" in driver.title
#====================================================================

#%%
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
#====================================================================

#%%
# Find the Password
p_word = driver.find_element(By.ID, "password")
# Clear the input
p_word.clear()
p_word.send_keys(password)
# Press Login
#====================================================================

#%%
# Use CSS selector for multiple classes
login_button = driver.find_element(By.CSS_SELECTOR, "button.btn__primary--large.from__button--floating")
# Add a delay of 1 seconds before entering password
time.sleep(1)
# Then click the button
login_button.click()
#====================================================================

#%%
# Wait for the search box to be present and clickable
wait = WebDriverWait(driver, 10)
search_box = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Search']"))
)

# Interact with the search box
search_box.clear()
search_box.send_keys("Mark Zuckerberg")

# Press Enter to submit the search
search_box.send_keys(Keys.RETURN)

# Optionally wait for search results to load
time.sleep(3)
#====================================================================

#%%
# Wait for the search results to load and the People filter button to be clickable
wait = WebDriverWait(driver, 10)
people_button = wait.until(
     EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search-reusables__filter-pill-button[aria-pressed='false']"))
)

# Click the People button
people_button.click()

# Wait for the filtered results to load
time.sleep(2)
#==========================================================================

#%%
# Wait for the "All filters" button to be present and clickable
wait = WebDriverWait(driver, 10)
all_filters_button = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search-reusables__all-filters-pill-button"))
)

# Click the "All filters" button
all_filters_button.click()

# Wait for the filter modal to appear
time.sleep(2)
#==========================================================================

#%%
# Wait for the "Add a school" button to be present and clickable within the School section
wait = WebDriverWait(driver, 10)

# Target the button by its ID - more reliable
try:
    # First try to use the ID which is the most reliable approach
    add_school_button = wait.until(
        EC.element_to_be_clickable((By.ID, "ember1281"))  # Using the ID from your HTML
    )
except:
    try:
        # If ID changes (which is likely), try targeting by the button text and its container
        add_school_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//fieldset[.//h3[text()='School']]//button[.//span[text()='Add a school']]"))
        )
    except:
        # Fallback to the simplest approach - find any button with "Add a school" text
        add_school_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-add-filter-button] span"))
        )
        # Find buttons with the Add a school text
        buttons = driver.find_elements(By.XPATH, "//button[.//span[text()='Add a school']]")
        if buttons:
            add_school_button = buttons[0]  # Take the first one

# Before clicking, make sure the button is in view
driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", add_school_button)
time.sleep(1)  # Give time for scrolling

# Click the "Add a school" button
add_school_button.click()

# Wait for the school input field to appear
time.sleep(2)

#%%
# Wait for the school input field to appear after clicking "Add a school"
wait = WebDriverWait(driver, 10)
school_input = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Add a school']"))
)

# Clear any existing text and enter the university name
school_input.clear()
school_input.send_keys("Western Mindanao State University")

# Wait for the typeahead suggestions to appear
time.sleep(2)

# Find and click on the suggestion dropdown div or option
try:
    # First try to find specific suggestion for the university
    suggestion = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.basic-typeahead__triggered-content div[role='option']"))
    )
    suggestion.click()
except:
    try:
        # If no specific option, try clicking the typeahead container
        typeahead_container = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.basic-typeahead__triggered-content"))
        )
        typeahead_container.click()
    except:
        # If still not found, just press down arrow and Enter as a fallback
        school_input.send_keys(Keys.DOWN)
        time.sleep(1)
        school_input.send_keys(Keys.RETURN)

# Wait for the selection to be processed
time.sleep(2)
#==========================================================================

#%%
# Wait for the "Show results" button to be present and clickable
wait = WebDriverWait(driver, 10)

try:
    # Try finding the button by its aria-label
    show_results_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Apply current filters to show results']"))
    )
except:
    # Fall back to previous approaches if aria-label doesn't work
    try:
        # Try with the data attribute
        show_results_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test-reusables-filters-modal-show-results-button='true']"))
        )
    except:
        # Try with the button's text content
        show_results_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Show results']]"))
        )

# Make sure the button is visible by scrolling to it
driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", show_results_button)
time.sleep(2)  # Give time for scrolling

# Try a direct JavaScript click
driver.execute_script("arguments[0].click();", show_results_button)

# Wait for the results page to load
time.sleep(5)
#==========================================================================

#%%
# Wait for search results to load
wait = WebDriverWait(driver, 5)

# Function to check if a search result matches our criteria
def find_and_click_matching_profile():
    # Get all search result elements
    search_results = driver.find_elements(By.CSS_SELECTOR, "div.reusable-search__result-container")
    
    for result in search_results:
        try:
            # Extract name and education info
            name_element = result.find_element(By.CSS_SELECTOR, "span.entity-result__title-text a")
            profile_name = name_element.text.strip()
            
            # Try to find education info
            try:
                education_element = result.find_element(By.CSS_SELECTOR, "div.entity-result__primary-subtitle, div.aFjBrNZtAQJlsDdweGlZDZXrbSCaQplKaU")
                education_text = education_element.text.strip()
            except:
                education_text = ""
                
            print(f"Checking profile: {profile_name}, Education: {education_text}")
            
            # Check if this result matches our criteria
            if "Attended Western Mindanao State University" in education_text:
                print(f"Found matching profile: {profile_name}")
                
                # Click on the profile or the Connect button
                try:
                    # Try to click the Connect button first if it exists
                    connect_button = result.find_element(By.XPATH, ".//button[contains(text(), 'Connect')]")
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", connect_button)
                    time.sleep(1)
                    connect_button.click()
                    print("Clicked Connect button")
                    return True
                except:
                    # If no Connect button, click the profile name
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", name_element)
                    time.sleep(1)
                    name_element.click()
                    print("Clicked profile name")
                    return True
        except Exception as e:
            print(f"Error processing a result: {str(e)}")
            continue
    
    return False

# Look for a matching profile in the search results
found_match = find_and_click_matching_profile()

if not found_match:
    print("No matching profiles found with Western Mindanao State University")

# Wait for possible navigation or modal dialog
time.sleep(5)
#==========================================================================
#%%

assert "No results found." not in driver.page_source
input("Press Enter to close the browser...")
driver.close()