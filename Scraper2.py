from linkedin_api import Linkedin
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
import random
import urllib.parse
import time
import dotenv
import os
def header():
    headers_list = [
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"},
        {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"},
    ]

    headers = random.choice(headers_list)
    return headers

def name_transfrom(name,form = 0):
    """
    0 - firstName-lastName
    1 - firstNameLastName

    """

    name = name.lower()
    if form == 0:
        transformed_name = name.lower().replace(" ", "-")
    elif form == 1:
        transformed_name = name.lower().replace(" ", "")

    # if 'ñ' in transformed_name:
    #     print(f"Found Spanish character 'ñ' in the name, encoding it for URL compatibility")
    #     # Replace ñ with the URL-encoded version
    #     transformed_name = transformed_name.replace('ñ', '%C3%B1')
    #     print(f"Encoded name: {transformed_name}")

    return transformed_name

def search_linkedin_posts(name, max_results=20):
    
    # Broader query to catch variations
    linkedInPost = "linkedin.com/posts/"
    query = f'{linkedInPost} {name}'
    print(f"name : {name}")
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.bing.com/search?q={encoded_query}"
    print(f"Searched Url : {url}")
    
    headers = header()
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    Web_Search_results = []
    


    #Iterate through search results
    for item in soup.find_all('li', {'class': 'b_algo'}):
        link = item.find('a')
        
        # Go to the link
        link2 = requests.get(link['href'], headers=headers)
    
        # Check if the link is valid and contains 'linkedin.com/posts/'
        if linkedInPost in link2.url:
            # print(f"Link2 url : {link2.url}")

            #check if the name is in the url
            for i in range(2):
                #transform the name based on the form
                transformed_name = name_transfrom(name, i)

                # print(f"Transformed Name: {transformed_name}")
                if transformed_name in link2.url:
                    # Web_Search_results.append(link2.url)
                    print(f"Found LinkedIn: {link2.url}")
                    
      
                    # Extract the profile ID from the URL
                    linkedin_parts = link2.url.split('linkedin.com/posts/')[1].split('_')[0]
                    # Remove any trailing characters if present
                    if '/' in linkedin_parts:
                        linkedin_parts = linkedin_parts.split('/')[0]
                    print(f"LinkedIn ID: {linkedin_parts}")
                    
                    # Check if the ID already exists in the results before adding
                    if linkedin_parts not in Web_Search_results:
                        Web_Search_results.append(linkedin_parts)
                        print(f"Added LinkedIn ID: {linkedin_parts}")
                    else:
                        print(f"Duplicate LinkedIn ID found: {linkedin_parts} (skipping)")

            
    return Web_Search_results


def search_linkedin_profile(name, max_results=20):
    
    # Broader query to catch variations
    linkedInProfile = "linkedin.com/in/"
    query = f'{linkedInProfile} {name}'
    print(f"name : {name}")

    # Encode the query for URL
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.bing.com/search?q={encoded_query}"
    print(f"Searched Url : {url}")
    
    headers = header()
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    Web_Search_results = []
    


    #Iterate through search results
    for item in soup.find_all('li', {'class': 'b_algo'}):
        link = item.find('a')
        # print(f"Link: {link['href']}")
        # Go to the link
        link2 = requests.get(link['href'], headers=headers)
        
        # Check if the link is valid and contains 'linkedin.com/in/'
        if linkedInProfile in link2.url:
            print(f"Link2 url : {link2.url}")

            #check if the name is in the url
            for i in range(2):
                #transform the name based on the form
                transformed_name = name_transfrom(name, i)
                # print(f"Transformed Name: {transformed_name}")
                print(f"Name : {transformed_name}")
                if transformed_name in link2.url:
                    print(f"Found LinkedIn: {link2.url}")
                    
                    # Extract the profile ID (only when matching name found)
                    linkedin_parts = link2.url.split('linkedin.com/in/')[1].split('_')[0]
                    # Remove any trailing characters if present
                    if '/' in linkedin_parts:
                        linkedin_parts = linkedin_parts.split('/')[0]
                    print(f"LinkedIn ID: {linkedin_parts}")
                    
                    # Add to results if unique
                    if linkedin_parts not in Web_Search_results:
                        Web_Search_results.append(linkedin_parts)
                        print(f"Added LinkedIn ID: {linkedin_parts}")
                    else:
                        print(f"Duplicate LinkedIn ID found: {linkedin_parts} (skipping)")
                else:
                    print(f"Not Found LinkedIn: {link2.url}")

            
    return Web_Search_results

def get_profile_details(profiles, email, password, target_school):
    """
    Get profile details using the LinkedIn API with rate limiting protection.
    
    Args:
        profiles: List of LinkedIn profile IDs to process
        email: LinkedIn login email
        password: LinkedIn login password
        target_school: School name to filter for (default: Western Mindanao State University)
       
    
    Returns:
        List of matching profiles with their details
    """
    if not profiles:
        print("No profiles to process")
        return []
        
    try:
        # Initialize the LinkedIn API
        api = Linkedin(email, password)
        results = []
        matching_results = []
        
        print(f"Looking for profiles from: {target_school}")
        
        
        # Process each profile with longer delays
        for i, profile in enumerate(profiles):
            print(f"Processing profile {i+1}/{len(profiles)}: {profile}")
            
            try:
                # Add random delay between 5-10 seconds to appear more human-like
                delay = random.randint(8, 15)  # Random delay between 8-15 seconds
                print(f"Waiting {delay} seconds before next request...")
                time.sleep(delay)
                
                # Get profile data with retry logic
                profile_data = None
                json_error_count = 0
                max_json_retries = 3
                
                while json_error_count < max_json_retries:
                    try:
                        profile_data = api.get_profile(profile)

                        # If we get here, the request was successful
                        break
                    except json.JSONDecodeError:
                        json_error_count += 1
                        print(f"JSON decode error for profile {profile} - retry {json_error_count}/{max_json_retries}")
                        
                        if json_error_count < max_json_retries:
                            retry_delay = 20  # 5 seconds between retries
                            print(f"Waiting {retry_delay} seconds before retry...")
                            time.sleep(retry_delay)
                        else:
                            print(f"Maximum retries reached for profile {profile} - moving to next profile")
                            # Add placeholder and take a longer break
                            results.append({
                                "username": profile,
                                "firstName": "",
                                "lastName": "",
                                "Latest job title": "Rate limited after multiple retries",
                                "Company": "",
                                "Role": "",
                                "Employment_Date": "",
                                "Education": "",
                                "Matched_Target_School": False,
                            })
                            print("Taking a longer break (30 seconds) due to persistent rate limiting...")
                            time.sleep(30)
                            continue
                
                # If we didn't get any profile data after all retries, move on
                if profile_data is None:
                    continue
                
                # Verify we got valid data
                if not isinstance(profile_data, dict):
                    print(f"Warning: Received invalid data for profile {profile}")
                    # Add a placeholder with username only
                    results.append({
                        "username": profile,
                        "firstName": "",
                        "lastName": "",
                        "Latest job title": "Data retrieval error",
                        "Company": "",
                        "Role": "",
                        "Employment_Date": "",
                        "Education": "",
                        "Matched_Target_School": False,
                    })
                    continue
                
                # Extract the information we need
                simplified_data = {
                    "username": profile,
                    "firstName": profile_data.get("firstName", ""),
                    "lastName": profile_data.get("lastName", ""),
                    "Latest job title": "",
                    "Company": "",
                    "Role": "",
                    "Employment_Date": "",
                    "Education": "",
                    "Matched_Target_School": False,
                }
                
                # Get the latest job information
                if profile_data.get("experience") and len(profile_data["experience"]) > 0:
                    # Experience entries are typically ordered with most recent first
                    latest_job = profile_data["experience"][0]
                    simplified_data["Latest job title"] = latest_job.get("title", "") or "NONE"
                    simplified_data["Company"] = latest_job.get("companyName", "") or "NONE"
                    
                    # Extract role information (description of job)
                    simplified_data["Role"] = latest_job.get("description", "") or "NONE"
                    
                    # Extract employment dates
                    time_period = latest_job.get("timePeriod", {})
                    start_date = time_period.get("startDate", {})
                    end_date = time_period.get("endDate", {})
                    
                    start_str = ""
                    if start_date:
                        month = start_date.get("month", "")
                        year = start_date.get("year", "")
                        if month and year:
                            start_str = f"{month}/{year}"
                        elif year:
                            start_str = f"{year}"
                    
                    end_str = "Present"
                    if end_date:
                        month = end_date.get("month", "")
                        year = end_date.get("year", "")
                        if month and year:
                            end_str = f"{month}/{year}"
                        elif year:
                            end_str = f"{year}"
                    
                    date_range = f"{start_str} - {end_str}" if start_str else ""
                    simplified_data["Employment_Date"] = date_range or "NONE"
                else:
                    # No experience data available
                    simplified_data["Latest job title"] = "NONE"
                    simplified_data["Company"] = "NONE"
                    simplified_data["Role"] = "NONE"
                    simplified_data["Employment_Date"] = "NONE"
                
                # Get the education information
                education_list = []
                matched_school = False
                
                if profile_data.get("education"):
                    for edu in profile_data["education"]:
                        school_name = edu.get("schoolName", "")
                        field_of_study = edu.get("fieldOfStudy", "")
                        
                        # Check for target school match
                        if target_school.lower() in school_name.lower():
                            matched_school = True
                            print(f"✓ School match found: {school_name}")
                            
                        
                        # Format the education entry
                        education_entry = []
                        if school_name:
                            education_entry.append(school_name)
                        if field_of_study:
                            education_entry.append(field_of_study)
                            
                        # Add dates if available
                        time_period = edu.get("timePeriod", {})
                        start_year = time_period.get("startDate", {}).get("year", "")
                        end_year = time_period.get("endDate", {}).get("year", "")
                        
                        if start_year and end_year:
                            education_entry.append(f"({start_year}-{end_year})")
                        elif start_year:
                            education_entry.append(f"(Started {start_year})")
                        elif end_year:
                            education_entry.append(f"(Graduated {end_year})")
                        
                        if education_entry:  # Only add if there's actual content
                            education_list.append(" - ".join(education_entry))

                # Set match flags
                simplified_data["Matched_Target_School"] = matched_school
                
                
                # Join all education entries with a separator
                simplified_data["Education"] = " | ".join(education_list) if education_list else "NONE"
                
                # Add to results
                results.append(simplified_data)
                
                # If this profile matches our criteria, add to matching results
                if matched_school:
                    matching_results.append(simplified_data)
                    print(f"⚠️ Profile matches school criteria: {profile}")
                else:
                    print(f"❌ Profile does NOT match target school: {profile}")
                
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
                    "Company": "",
                    "Role": "",
                    "Employment_Date": "",
                    "Education": "",
                    "Matched_Target_School": False,
                })
                
                # If we get multiple errors in sequence, take a very long break
                if i > 0 and "Error processing profile" in locals().get('last_message', ''):
                    recovery_time = 60
                    print(f"Multiple errors in sequence. Taking a {recovery_time}-second break to recover...")
                    time.sleep(recovery_time)
                
                last_message = f"Error processing profile {profile}"
        
        # Report on matches
        print(f"Found {sum(1 for r in results if r['Matched_Target_School'])} profiles from {target_school}")

        # Return only matching profiles if any, otherwise return empty list
        if matching_results:
            return matching_results
        else:
            print("No profiles match both school criteria - returning empty list")
            return []  # Return empty list instead of all profiles
        
    except Exception as e:
        print(f"Error initializing LinkedIn API: {str(e)}")
        return []
    

def get_names_from_excel(excel_path="linkedin_profiles.xlsx"):
    """
    Get a list of names from the "Names" column in the specified Excel file.
    
    Args:
        excel_path: Path to the Excel file (default: "linkedin_profiles.xlsx")
        
    Returns:
        List of names from the Excel file's "Names" column
    """
    try:
        # Read the Excel file
        print(f"Reading names from: {excel_path}")
        df = pd.read_excel(excel_path)
        
        # Check if "Names" column exists
        if "Names" not in df.columns:
            print(f"Error: No 'Names' column found in {excel_path}")
            return []
            
        # Extract names from the "Names" column, skip empty cells
        names = [name for name in df["Names"].tolist() if isinstance(name, str) or not pd.isna(name)]
        
        print(f"Found {len(names)} names in the Excel file")
        return names
        
    except FileNotFoundError:
        print(f"Error: File '{excel_path}' not found")
        return []
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        return []
    
dotenv.load_dotenv()
Email = os.getenv("Email")
Password = os.getenv("Password")
School = "Western Mindanao State University"
max_attempt = 3

# Get names from Excel file
names = get_names_from_excel("linkedin_profiles.xlsx")

# Initialize a dictionary to store details for all names
all_details = {}

for name_index, Name in enumerate(names):
    print(f"\n{'='*80}")
    print(f"Processing name {name_index+1}/{len(names)}: {Name}")
    print(f"{'='*80}\n")
    
    attempt = 0
    profiles = None
    details = None
    
    # Filter the name to remove middle initials if needed
    filtered_name = Name
    name_parts = Name.split()
    
    # Check if there are more than 2 parts and the middle part looks like an initial
    if len(name_parts) > 2:
        # Middle initial pattern: single letter possibly followed by a period
        for i in range(1, len(name_parts) - 1):
            part = name_parts[i]
            if len(part) == 1 or (len(part) == 2 and part[1] == '.'):
                # Remove this part as it's likely a middle initial
                filtered_name = ' '.join(name_parts[:i] + name_parts[i+1:])
                print(f"Removed middle initial: '{Name}' -> '{filtered_name}'")
                Name = filtered_name
                break
    


    if filtered_name != Name:
        print(f"Using filtered name: {filtered_name}")

        

    time.sleep(30) # Wait a moment before starting the search
    print("Starting LinkedIn Profile Search...")
    # First attempt: Search for LinkedIn profiles
    for i in range(max_attempt):
        print(f"Attempt {i+1}/{max_attempt} to find LinkedIn profiles for {Name}...")
        profiles = search_linkedin_profile(Name)
        if profiles:
            print(f"Found {len(profiles)} LinkedIn profiles on attempt {i+1}.")
            break
        time.sleep(10)# Wait a moment before next attempt

    # Process profiles if found
    if profiles:
        print("Found LinkedIn Profiles:")
        for i, url in enumerate(profiles, 1):
            print(f"{i}. {url}")

        details = get_profile_details(profiles, Email, Password, School)

        # If no details found, try posts search
        if not details:
            print("No profile details found, trying posts search...")
            profiles = None  # Clear profiles to try posts search
            
            # Second attempt: Search for LinkedIn posts when details weren't found
            for i in range(max_attempt):
                print(f"Attempt {i+1}/{max_attempt} to find LinkedIn post for {Name}...")
                profiles = search_linkedin_posts(Name)
                if profiles:
                    print(f"Found {len(profiles)} LinkedIn posts on attempt {i+1}.")
                    break
                time.sleep(10)  # Wait a moment before next attempt

            if profiles:
                print("Found LinkedIn Profiles through posts:")
                for i, url in enumerate(profiles, 1):
                    print(f"{i}. {url}")
                
                details = get_profile_details(profiles, Email, Password, School)
            else:
                print("No LinkedIn profiles found through posts.")
    else:
        # Third attempt: Search for LinkedIn posts when no profiles were found
        print("No LinkedIn profiles found through Profile.")
        print("Finding profile URL through posts.")

        print("Waiting a moment before trying posts search...")
        for i in range(3, 0, -1):
            print(f"Continuing in {i}...")
            time.sleep(10)

        print("Searching LinkedIn posts for the name...")

        for i in range(max_attempt):
            print(f"Attempt {i+1}/{max_attempt} to find LinkedIn post for {Name}...")
            profiles = search_linkedin_posts(Name)
            if profiles:
                print(f"Found {len(profiles)} LinkedIn posts on attempt {i+1}.")
                break
            time.sleep(10)  # Wait a moment before next attempt

        if profiles:
            print("Found LinkedIn Profiles:")
            for i, url in enumerate(profiles, 1):
                print(f"{i}. {url}")
            
            details = get_profile_details(profiles, Email, Password, School)
        else:
            print("No LinkedIn profiles found through posts.")

    # Print results from profile details
    if 'details' in locals() and details:
        all_details[Name] = details
        print(f"\nDetails found for {Name}:")
    else:
        all_details[Name] = []  # Add an empty list for names with no profiles
        print("\nError: No profile details found for this name.")

    
    


# After processing all names, update the Excel file with results
print(f"\n{'='*80}")
print("Updating Excel file with LinkedIn data...")
print(f"{'='*80}\n")

# Replace your existing Excel update code with this:
try:
    # Read the original Excel file
    excel_path = "linkedin_profiles.xlsx"
    df = pd.read_excel(excel_path)
    
    # Add new columns if they don't exist - explicitly set string dtype
    new_columns = ["LinkedIn Profile", "Job Title", "Company", "Employment Date", "Education"]
    for col in new_columns:
        if col not in df.columns:
            df[col] = ""
        else:
            # Convert existing columns to string type to avoid dtype warnings
            df[col] = df[col].astype(str)
    
    # Update the Excel file with results for each name
    updated_count = 0
    for i, row in df.iterrows():
        name = row["Names"].strip() if isinstance(row["Names"], str) else ""
        if not name:
            continue
            
        # Debug deep output to see what data we have for this name
        print(f"Processing Excel row for: '{name}'")
        print(f"- Has data in all_details: {name in all_details}")
        if name in all_details:
            print(f"- Number of profiles: {len(all_details[name])}")
            if len(all_details[name]) > 0:
                print(f"- Profile data: {all_details[name][0]['username']}")
        
        # Check if we have profile data for this specific name
        if name in all_details and len(all_details[name]) > 0:
            profile = all_details[name][0]  # Get first profile
            
            # Verify it's the right profile before applying
            print(f"- Matched profile username: {profile['username']}")
            
            # Update the row with LinkedIn data
            df.at[i, "LinkedIn Profile"] = str(f"https://www.linkedin.com/in/{profile['username']}")
            df.at[i, "Job Title"] = str(profile["Latest job title"])
            df.at[i, "Company"] = str(profile["Company"])
            df.at[i, "Employment Date"] = str(profile["Employment_Date"])
            df.at[i, "Education"] = str(profile["Education"])
            
            updated_count += 1
            print(f"✅ Updated row for: {name}")
        else:
            # Clear data and set to "Not found"
            df.at[i, "LinkedIn Profile"] = "Not found"
            df.at[i, "Job Title"] = "Not found"
            df.at[i, "Company"] = "Not found"
            df.at[i, "Employment Date"] = "Not found"
            df.at[i, "Education"] = "Not found"
            print(f"❌ No profile data for: {name}")
    
    # Save the updated DataFrame back to Excel
    df.to_excel(excel_path, index=False)
    print(f"Successfully updated {updated_count} rows in {excel_path}")
except Exception as e:
    print(f"Error updating Excel file: {str(e)}")
