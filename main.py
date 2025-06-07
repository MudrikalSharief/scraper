#   Type in terminal
# pip install virtualenv	
# virtuaenv env
# .\env\Scripts\activate.ps1
# if the env is active insall
# pip install linkedin-api
# pip install pandas openpyxl
#
#put in the same folder as this file the excel file with the name must be "linkedin_profiles.xlsx
# the excel file must have a column with the name "username" or the first column will be used
#
#
from linkedin_api import Linkedin
import json
import pandas as pd

# Read LinkedIn usernames from Excel file
try:
    # Assumes Excel file has a column named "username" or that you want the first column
    excel_data = pd.read_excel("linkedin_profiles.xlsx")
    
    # If your column with usernames is named "username"
    if "username" in excel_data.columns:
        profiles = excel_data["username"].tolist()
    else:
        # Otherwise take first column
        profiles = excel_data.iloc[:, 0].tolist()
    
    # Remove any NaN values
    profiles = [p for p in profiles if isinstance(p, str)]
    
    print(f"Loaded {len(profiles)} profiles from Excel")
except Exception as e:
    print(f"Error loading Excel file: {str(e)}")
    profiles = []

api = Linkedin('shariefkundo19@gmail.com','*Lakirdum19*')

results = []

for profile in profiles:
    print(f"Processing profile: {profile}")
    
    try:
        # Get profile data
        profile_data = api.get_profile(profile)
        
        # Extract only the information we need
        simplified_data = {
            "username": profile,
            "firstName": profile_data.get("firstName", ""),
            "lastName": profile_data.get("lastName", ""),
            "Latest job title": "",  # Initialize with empty values
            "Company": ""
        }
        
        # Get the latest job information
        if profile_data.get("experience") and len(profile_data["experience"]) > 0:
            # Experience entries are typically ordered with most recent first
            latest_job = profile_data["experience"][0]
            job_title = latest_job.get("title", "")
            company_name = latest_job.get("companyName", "")
            
            # Add to the simplified data
            simplified_data["Latest job title"] = job_title
            simplified_data["Company"] = company_name
            
            # Keep the latestJob structure for JSON output
            simplified_data["latestJob"] = {
                "title": job_title,
                "company": company_name,
                "startDate": latest_job.get("timePeriod", {}).get("startDate", {})
            }
        else:
            simplified_data["latestJob"] = None
            
        results.append(simplified_data)
    except Exception as e:
        print(f"Error processing profile {profile}: {str(e)}")

# Output all results as JSON
print(json.dumps(results, indent=4))
# Save to CSV file with the specified column names
try:
    # Create a DataFrame from the results
    df = pd.DataFrame(results)
    
    # Create a new column that merges first and last name, handling potential missing values
    df["Full Name"] = df["firstName"].fillna("") + " " + df["lastName"].fillna("")
    df["Full Name"] = df["Full Name"].str.strip()  # Remove extra spaces
    
    # Select and order columns for the CSV
    columns_to_save = ["Full Name", "Latest job title", "Company"]
    
    # Save to CSV
    df[columns_to_save].to_csv("linkedin_profiles_results.csv", index=False)
    print("Results saved to linkedin_profiles_results.csv")
except Exception as e:
    print(f"Error saving results to CSV: {str(e)}")

