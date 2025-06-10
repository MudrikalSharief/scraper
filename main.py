# LinkedIn Profile Scraper
# Requirements:
# pip install linkedin-api pandas openpyxl selenium python-dotenv serpapi

from linkedin_api import Linkedin
import pandas as pd
import json
import os
import re
import time
import dotenv
from serpapi import GoogleSearch

# Load environment variables from .env file
dotenv.load_dotenv()
EMAIL = os.getenv("email")
PASSWORD = os.getenv("password")
API_KEY = os.getenv("SerApiKey")
SCHOOL = "Western Mindanao State University"
EXCEL_FILE = "linkedin_profiles.xlsx"
RESULTS_FILE = "linkedin_profiles_results.csv"

def get_first_linkedin_profile(name, school):
    """Search for a LinkedIn profile using SerpAPI and return the first match."""
    query = f'site:linkedin.com/in/ "{name}" "{school}"'
    
    try:
        search = GoogleSearch({
            "q": query,
            "api_key": API_KEY
        })

        results = search.get_dict()
        for result in results.get("organic_results", []):
            link = result.get("link", "")
            if "linkedin.com/in/" in link:
                # Extract name from link for verification
                match = re.search(r'linkedin\.com/in/([^/?]+)', link)
                if match:
                    username = match.group(1)
                    # Convert both to lowercase and remove spaces/special characters for comparison
                    normalized_name = re.sub(r'[^a-z0-9]', '', name.lower())
                    normalized_username = re.sub(r'[^a-z0-9]', '', username.lower())
                    
                    # Check if at least part of the name appears in the username
                    name_parts = normalized_name.split()
                    name_in_link = False
                    
                    # Check if any part of the name is in the username
                    for part in name_parts:
                        if len(part) > 2 and part in normalized_username:  # Only check parts longer than 2 chars
                            name_in_link = True
                            break
                    
                    # Also check if first letter of first and last name match pattern in username
                    name_words = name.lower().split()
                    if len(name_words) >= 2:
                        first_initial = name_words[0][0] if name_words[0] else ""
                        last_initial = name_words[-1][0] if name_words[-1] else ""
                        
                        # Check for patterns like "jsmith" (first initial + last name)
                        if first_initial and normalized_username.startswith(first_initial) and any(word[1:] in normalized_username for word in name_words if len(word) > 1):
                            name_in_link = True
                    
                    if name_in_link:
                        print(f"Found matching profile for {name}: {link}")
                        return link
                    else:
                        print(f"Found profile but name verification failed. Link: {link}, Name: {name}")
                        # Continue searching for a better match
    except Exception as e:
        print(f"SerpAPI search error for {name}: {str(e)}")
    
    return "NONE"

def collect_linkedin_links(excel_path, school_name):
    """Process the Excel file to find LinkedIn profiles for each name."""
    try:
        # Check if file exists
        if not os.path.exists(excel_path):
            print(f"Error: File '{excel_path}' not found.")
            return False
            
        try:
            # Read the Excel file
            df = pd.read_excel(excel_path)
        except PermissionError:
            print(f"Error: Cannot open '{excel_path}'. Make sure it's not open in another program.")
            return False
        
        # Check if the 'Names' column exists
        if 'Names' not in df.columns:
            print("Error: Excel file must contain a 'Names' column")
            return False
            
        # Create 'LinkedIn_Link' column if it doesn't exist
        if 'LinkedIn_Link' not in df.columns:
            print("Creating new 'LinkedIn_Link' column")
            df['LinkedIn_Link'] = None
        else:
            print("'LinkedIn_Link' column already exists, will skip names with existing links")
        
        # Track progress
        total_names = len(df)
        processed = 0
        skipped = 0
        
        # Process each row
        for index, row in df.iterrows():
            name = row['Names']
            
            # Skip if the name is empty
            if pd.isna(name):
                print(f"Skipping row {index+1}: Empty name")
                skipped += 1
                continue
                
            # Skip if link already exists
            if not pd.isna(row.get('LinkedIn_Link')):
                print(f"Skipping row {index+1}: '{name}' already has a link")
                skipped += 1
                continue
            
            processed += 1    
            print(f"Processing {processed}/{total_names-skipped} ({index+1}/{total_names} total): {name}")
            
            # Get LinkedIn profile link
            link = get_first_linkedin_profile(name, school_name)
            
            # Update the dataframe
            df.at[index, 'LinkedIn_Link'] = link
            
            # Save after each search to avoid losing data if there's an error
            try:
                df.to_excel(excel_path, index=False)
                print(f"Saved progress for '{name}': {link}")
            except Exception as save_error:
                # Try saving to a different file if original is locked
                backup_path = excel_path.replace('.xlsx', '_backup.xlsx')
                print(f"Could not save to original file. Saving to {backup_path}")
                df.to_excel(backup_path, index=False)
            
            # Add a delay to avoid hitting rate limits
            time.sleep(2)
        
        print(f"Processing complete. Processed {processed} names, skipped {skipped} names.")
        print(f"Results saved to {excel_path}")
        return True
        
    except Exception as e:
        print(f"Error processing Excel file: {str(e)}")
        return False

def extract_linkedin_usernames(excel_path):
    """Extract LinkedIn usernames from URLs in the Excel file."""
    try:
        # Read the Excel file
        excel_data = pd.read_excel(excel_path)
        profiles = []

        # Check if LinkedIn_Link column exists
        if "LinkedIn_Link" in excel_data.columns:
            raw_links = excel_data["LinkedIn_Link"].tolist()
            
            # Process each link to extract just the username part
            for link in raw_links:
                # Skip if not a string (NaN, None, etc.) or "NONE"
                if not isinstance(link, str) or link == "NONE":
                    continue
                    
                # Extract username part from URL using regex
                if "linkedin.com/in/" in link:
                    match = re.search(r'linkedin\.com/in/([^/?]+)', link)
                    if match:
                        username = match.group(1)
                        # Remove trailing slash if present
                        if username.endswith('/'):
                            username = username[:-1]
                        profiles.append(username)
                        print(f"Extracted username: {username}")
                    else:
                        print(f"Could not extract username from: {link}")
                elif link != "NONE":
                    # If it doesn't look like a LinkedIn URL but isn't "NONE", use as-is
                    profiles.append(link)
                    print(f"Using as-is: {link}")
        else:
            print("No LinkedIn_Link column found in Excel file")
            return []
        
        print(f"Loaded {len(profiles)} valid profiles from Excel")
        return profiles
        
    except Exception as e:
        print(f"Error extracting usernames: {str(e)}")
        return []

def get_profile_details(profiles, email, password):
    """Get profile details using the LinkedIn API with rate limiting protection."""
    if not profiles:
        print("No profiles to process")
        return []
        
    try:
        # Initialize the LinkedIn API
        api = Linkedin(email, password)
        results = []
        
        # Process each profile with longer delays
        for i, profile in enumerate(profiles):
            print(f"Processing profile {i+1}/{len(profiles)}: {profile}")
            
            try:
                # Add random delay between 5-10 seconds to appear more human-like
                delay = 5 + (i % 5)  # Varies between 5-9 seconds
                print(f"Waiting {delay} seconds before next request...")
                time.sleep(delay)
                
                try:
                    # Get profile data
                    profile_data = api.get_profile(profile)
                    
                    # Verify we got valid data
                    if not profile_data or not isinstance(profile_data, dict):
                        print(f"Warning: Received invalid data for profile {profile}")
                        # Add a placeholder with username only
                        results.append({
                            "username": profile,
                            "firstName": "",
                            "lastName": "",
                            "Latest job title": "Data retrieval error",
                            "Company": ""
                        })
                        continue
                        
                except json.JSONDecodeError:
                    print(f"JSON decode error for profile {profile} - likely rate limited")
                    # Add placeholder and take a longer break
                    results.append({
                        "username": profile,
                        "firstName": "",
                        "lastName": "",
                        "Latest job title": "Rate limited",
                        "Company": ""
                    })
                    print("Taking a longer break (30 seconds) due to possible rate limiting...")
                    time.sleep(30)
                    continue
                
                # Extract the information we need
                simplified_data = {
                    "username": profile,
                    "firstName": profile_data.get("firstName", ""),
                    "lastName": profile_data.get("lastName", ""),
                    "Latest job title": "",
                    "Company": ""
                }
                
                # Get the latest job information
                if profile_data.get("experience") and len(profile_data["experience"]) > 0:
                    # Experience entries are typically ordered with most recent first
                    latest_job = profile_data["experience"][0]
                    simplified_data["Latest job title"] = latest_job.get("title", "")
                    simplified_data["Company"] = latest_job.get("companyName", "")
                
                results.append(simplified_data)
                print(f"Successfully processed {profile}")
                
                # Add a longer pause after every 5 profiles
                if (i + 1) % 5 == 0 and i < len(profiles) - 1:
                    pause_time = 20
                    print(f"Taking a {pause_time}-second break after processing 5 profiles...")
                    time.sleep(pause_time)
                
            except Exception as e:
                print(f"Error processing profile {profile}: {str(e)}")
                # Add the profile to results with error indication
                results.append({
                    "username": profile,
                    "firstName": "",
                    "lastName": "",
                    "Latest job title": f"Error: {str(e)[:50]}",
                    "Company": ""
                })
                
                # If we get multiple errors in sequence, take a very long break
                if i > 0 and "Error processing profile" in locals().get('last_message', ''):
                    recovery_time = 60
                    print(f"Multiple errors in sequence. Taking a {recovery_time}-second break to recover...")
                    time.sleep(recovery_time)
                
                last_message = f"Error processing profile {profile}"
        
        return results
        
    except Exception as e:
        print(f"Error initializing LinkedIn API: {str(e)}")
        return []

def save_results_to_excel(results, excel_path):
    """Save the results back to the original Excel file."""
    if not results:
        print("No results to save")
        return False
        
    try:
        # Try to read the existing Excel file
        try:
            df = pd.read_excel(excel_path)
        except PermissionError:
            print(f"Error: Cannot open '{excel_path}'. Make sure it's not open in another program.")
            backup_path = excel_path.replace('.xlsx', '_with_results.xlsx')
            print(f"Will save to {backup_path} instead")
            return save_results_to_excel(results, backup_path)
        
        # Check if the required columns exist, if not, create them
        if 'Job_Title' not in df.columns:
            df['Job_Title'] = None
        if 'Company' not in df.columns:
            df['Company'] = None
        
        # Create a lookup dictionary for easier matching
        profile_data = {}
        for result in results:
            username = result.get('username', '')
            profile_data[username] = {
                'job_title': result.get('Latest job title', 'NONE'),
                'company': result.get('Company', 'NONE')
            }
        
        # Add data to the Excel file based on matching usernames
        for index, row in df.iterrows():
            link = row.get('LinkedIn_Link', '')
            
            # Skip if no link or "NONE"
            if not isinstance(link, str) or link == "NONE":
                continue
            
            # Extract username from LinkedIn link
            username = None
            if "linkedin.com/in/" in link:
                match = re.search(r'linkedin\.com/in/([^/?]+)', link)
                if match:
                    username = match.group(1)
                    # Remove trailing slash if present
                    if username.endswith('/'):
                        username = username[:-1]
            
            # Update the row if we have data for this username
            if username and username in profile_data:
                df.at[index, 'Job_Title'] = profile_data[username]['job_title']
                df.at[index, 'Company'] = profile_data[username]['company']
        
        # Save the updated DataFrame back to the Excel file
        try:
            df.to_excel(excel_path, index=False)
            print(f"Results saved back to original file: {excel_path}")
            return True
        except Exception as save_error:
            # If saving fails, try a different filename
            backup_path = excel_path.replace('.xlsx', '_with_results.xlsx')
            print(f"Could not save to original file. Saving to {backup_path}")
            df.to_excel(backup_path, index=False)
            print(f"Results saved to {backup_path}")
            return True
        
    except Exception as e:
        print(f"Error saving results to Excel: {str(e)}")
        return False

def main():
    """Main function to run the LinkedIn profile scraper."""
    # Step 1: Check if we need to collect LinkedIn links
    should_collect = input("Do you want to search for LinkedIn profiles? (y/n): ").lower() == 'y'
    if should_collect:
        collect_linkedin_links(EXCEL_FILE, SCHOOL)
    
    # Step 2: Extract LinkedIn usernames from the links
    profiles = extract_linkedin_usernames(EXCEL_FILE)
    
    # Step 3: Get profile details using the LinkedIn API
    if profiles:
        results = get_profile_details(profiles, EMAIL, PASSWORD)
        
        # Step 4: Save results back to the original Excel file
        if results:
            save_results_to_excel(results, EXCEL_FILE)

if __name__ == "__main__":
    main()