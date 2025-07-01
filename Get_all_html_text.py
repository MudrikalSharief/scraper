from bs4 import BeautifulSoup
import random
import requests
import os
import time
import socket
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import pandas as pd

import json
import re
from google import genai
from google.genai import types
import dotenv
from dotenv import load_dotenv
from PIL import Image # Import Pillow
import sys
load_dotenv()

#gemini part function ==============================================================================


def generate(text, journal_name, website_url):
    """Generate content using only text (no images), switching API keys if quota is reached."""
    # List your Gemini API keys here (from environment or hardcoded)
    api_keys = [
        os.environ.get("GeminiKey"),
        os.environ.get("GeminiKey2"),
        os.environ.get("GeminiKey3"),
        os.environ.get("GeminiKey4"),
        # Add more keys as needed
    ]
    last_error = None

    for api_key in api_keys:
        if not api_key:
            continue  # Skip empty keys
        print(f"Using API key #{api_keys.index(api_key) + 1}...")  # Print the index + 1 of the current API key
        
        client = genai.Client(api_key=api_key)

        prompt_part1 = f"""
        You are an expert AI Journal Scraper and Data Extractor. Your task is to analyze the provided text from a journal's website and extract specific information about it.

        Your goal is to fill in the details for the following fields. For fields with predefined choices, you MUST select one of the provided options. If information for a field is not explicitly found or cannot be confidently inferred from the text, mark its value as "Unknown" or "Not Applicable" where specified.

        Present the extracted information in a structured JSON format.

        ---

        **
        {text}
        **

        ---

        **Extraction Fields and Rules:**
        """

        json_template = f"""```json
        {{
          "Journal Name": "{journal_name}",
          "Publisher Name": "...",
          "ISSN": "...",
          "Website URL": "{website_url}",
          "Editorial Board Members": "...",
          "Peer Review Process": "...",
          "Publishing Model": "...",
          "Publication Fees/Article Processing Fees": "...",
          "Publication Frequency": "...",
          "DOI Availability": "...",
          "Indexing": "...",
          "Editorial Process Transparency": "...",
          "Journal's Scope & Aims": "...",
          "Calls for Papers (CFPs)": "...",
          "Year Established": "...",
          "Journal's Acceptance Rate": "...",
          "Publication Days": "...",
          "Cite Score": "...",
          "Impact Factor": "...",
          "Include Author Guidelines": "...",
          "Submission Process": "...",
          "Publication Ethics": "...",
          "University Affiliation": "...",
          "Name of University": "..."
        }}```"""

        extraction_rules = """
        1.  **Journal Name:** The full name of the journal.
        2.  **Publisher Name:** The name of the organization that publishes the journal. if not mentioned, state "NONE".
        3.  **ISSN:** The International Standard Serial Number (can be print ISSN or online ISSN just select one and dont stae if online or printed just the number), if not found state NONE.
        4.  **Website URL:** The primary URL of the journal's website (this should be the URL the input text came from).
        5.  **Editorial Board Members:** (Listed, Unknown) - Is a list of editorial board members explicitly available and clearly presented if yes then put listed else put unknown?
        6.  **Peer Review Process:** (Single Blind, Double Blind, Open Peer Review, Unknown) - How does the journal describe its peer review process? if not mentioned or unclear, state "Unknown".
        7.  **Publishing Model:** (Open Access, Subscription, Unknown) - How does the journal make its content available?
        8.  **Publication Fees/Article Processing Fees:** The amount or range of fees charged to authors. If "No fees," state "0". If present but specific amount unknown, state "-1". If not mentioned, state "-1" please only get payment with dollar or $ if not in dollar please convert it to dollar. type it like this $300.
        9.  **Publication Frequency:** (Weekly, Monthly, Twice a month, Quarterly, Twice every quarter, Yearly, Twice a year, 3 times a year, Unknown) - How often does the journal publish new issues?
        10. **DOI Availability:** (Yes, No, Unknown) - Does the journal explicitly mention assigning DOIs (Digital Object Identifiers) to its articles?
        11. **Indexing:** (Scopus, Web of Science, DOAJ, Google, Others, Unknown) - put only 1 prioritize the order given explicitly mentioned indexing services. If "Others" is chosen state "Others", state "Unknown".
        12. **Editorial Process Transparency:** (Listed, Unknown) - Is the editorial process (beyond peer review) clearly described and transparently presented on the website?
        13. **Journal's Scope & Aims:** (Domain-specific, Multi-disciplinary, Broad, Unknown) - Select the journal's stated scope and aims from the following options: Domain-specific, Multi-disciplinary, Broad, Unknown.
        14. **Calls for Papers (CFPs):** (Weekly, Monthly, Twice a Month, Quarterly, Twice every Quarter, Yearly, Twice a Year, 3 Times a Year, Unknown) - How often does the journal issue calls for papers?
        15. **Year Established:** The year the journal was founded or first published. if not stated, state "-1". If the year is mentioned but not specific, use "-1". If the journal is newly established and the year is not mentioned, also use "-1".
        16. **Journal's Acceptance Rate:** The stated acceptance rate (e.g., "30%"). If not stated, "Unknown".
        17. **Publication Days:** The typical number of days from submission to publication, if separated please add them. If not stated or cannot be confidently inferred, "Unknown".
        18. **Cite Score:** The journal's stated CiteScore. If not stated, state "-1".
        19. **Impact Factor:** find the journal's stated Impact Factor, if not stated state"-1".
        20. **Include Author Guidelines:** (Yes, No, Unknown) - Are clear guidelines for authors explicitly provided on the website?
        21. **Submission Process:** (System, Email, Unknown) - How do authors submit their manuscripts? (e.g., through an online submission system, via email).
        22. **Publication Ethics:** (Listed, Unknown) - Does the journal have a clearly stated section on publication ethics or adherence to ethical guidelines (e.g., COPE)?
        23. **University Affiliation:** (Yes, No, Unknown) - Does the journal claim or show a clear affiliation with a university?
        24. **Name of University:** (If "University Affiliation" is "Yes", state the full name of the university just put 1 university incase there are more than 1  . Otherwise, put "NONE").

        ---

        **Output Format (JSON):**"""

        parts = [
            types.Part(text=prompt_part1),
            types.Part(text=extraction_rules),
            types.Part(text=json_template)
        ]

        model = "gemini-2.5-flash"

        contents = [
            types.Content(
                role="user",
                parts=parts
            ),
        ]

        generate_content_config = types.GenerateContentConfig(
            thinking_config = types.ThinkingConfig(
                thinking_budget=0,
            ),
            response_mime_type="text/plain",
        )

        full_response = ""
        try:
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                if chunk.text is not None:
                    print(chunk.text, end="")
                    full_response += chunk.text
            return full_response  # Success, return response
        except Exception as e:
            error_message = str(e)
            print(f"\nError during Gemini API call with current key: {e}")
            # Check for resource exhausted (quota/credit limit)
            if "RESOURCE_EXHAUSTED" in error_message or "quota" in error_message.lower():
                print("Quota exhausted for this API key, trying next key...")
                last_error = error_message
                continue  # Try next key
            else:
                # For other errors, break and return
                print("Non-quota error, aborting further attempts.")
                break

    # If all keys fail
    print("All API keys failed or quota exhausted.")
    if last_error:
        print(f"Last error: {last_error}")
    sys.exit("Exiting due to API errors. Please check your API keys or quota limits.")
    return None

def extract_json_from_response(response_text):
    """Extract JSON from the Gemini response text"""
    json_pattern = r"```json\s*(.*?)```"
    json_match = re.search(json_pattern, response_text, re.DOTALL)
    
    if json_match:
        json_str = json_match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"JSON string that failed to parse: {json_str}")
            return None
    else:
        print("No JSON found in response")
        return None

def save_to_excel(json_data, output_file):
    """Save the extracted JSON data to an Excel file, appending if file exists."""
    try:
        new_df = pd.DataFrame([json_data])

        if os.path.exists(output_file):
            try:
                existing_df = pd.read_excel(output_file)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            except Exception as e:
                print(f"Error reading existing Excel file: {e}")
                combined_df = new_df
        else:
            combined_df = new_df

        combined_df.to_excel(output_file, index=False)
        print(f"Data successfully saved to {output_file}")

    except Exception as e:
        print(f"Error saving to Excel: {e}")

def get_empty_gemini_row(journal_name, website_url):
    return {
        "Journal Name": journal_name,
        "Publisher Name": "NONE",
        "ISSN": "NONE",
        "Website URL": website_url,
        "Editorial Board Members": "Unknown",
        "Peer Review Process": "Unknown",
        "Publishing Model": "Unknown",
        "Publication Fees/Article Processing Fees": -1,
        "Publication Frequency": "Unknown",
        "DOI Availability": "Unknown",
        "Indexing": "Unknown",
        "Editorial Process Transparency": "Unknown",
        "Journal's Scope & Aims": "Unknown",
        "Calls for Papers (CFPs)": "Unknown",
        "Year Established": -1,
        "Journal's Acceptance Rate": "Unknown",
        "Publication Days": "Unknown",
        "Cite Score": -1,
        "Impact Factor": -1,
        "Include Author Guidelines": "Unknown",
        "Submission Process": "Unknown",
        "Publication Ethics": "Unknown",
        "University Affiliation": "Unknown",
        "Name of University": "NONE"
    }

def is_text_empty_or_none(text=None, file_name=None, folder_path='downloaded_texts'):
    """
    Returns True if the text is empty, contains only whitespace, or contains 'NONE' (case-insensitive).
    Can check either a direct text input or a file inside the specified folder.
    """
    # If text is directly provided
    if text is not None:
        if not text or str(text).strip() == "" or str(text).strip().upper() == "NONE":
            return True
        return False
    
    # If file_name is provided, read the file and check its content
    if file_name is not None:
        file_path = os.path.join(folder_path, file_name)
        if not file_name.endswith('.txt'):
            file_path += '.txt'
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if not content or content.strip() == "" or content.strip().upper() == "NONE":
                        return True
                return False
            else:
                print(f"File not found: {file_path}")
                return True  # Consider a non-existent file as empty
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return True  # Consider error in file reading as empty
    
    # Default case if neither text nor file_name is provided
    return True

def get_text_from_folder(folder_path = 'downloaded_texts', file_name='Name of the Journal'):
    
    specific_file = file_name  # Replace with your specific file name
    
    if specific_file.endswith('.txt'):
        specific_file = specific_file
    else:
        specific_file = specific_file + '.txt'

    file_path = os.path.join(folder_path, specific_file)
    print(f"Looking for file: {file_path}")

    if os.path.exists(file_path) and file_path.endswith(".txt"):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text_content = file.read()
            print(f"Processing file: {specific_file}")
            return text_content
        except Exception as e:
            print(f"Error reading file {specific_file}: {e}")
            text_content = ""
            return False
    else:
        print(f"File not found or not a text file: {specific_file}")
        text_content = ""
        return False

def save_json_to_excel(journal_name, website_url, excel_name, folder='downloaded_texts'):
    
    text_content = get_text_from_folder(folder, file_name=journal_name)

    if is_text_empty_or_none(text=text_content, file_name=journal_name, folder_path=folder):
        print("Text is empty or contains NONE")
        # Save a blank row with correct defaults
        save_to_excel(get_empty_gemini_row(journal_name, website_url), excel_name)
    else:
        try:
            response = generate(text_content, journal_name, website_url)
            if response:
                json_data = extract_json_from_response(response)
            
                # Ensure the key fields are populated with provided values if they're missing
                if json_data:
                    if not json_data.get("Journal Name") or json_data["Journal Name"] == "NONE":
                        json_data["Journal Name"] = journal_name
                    
                    if not json_data.get("Website URL") or json_data["Website URL"] == "NONE":
                        json_data["Website URL"] = website_url
                
                if json_data:
                    save_to_excel(json_data, excel_name)
                else:
                    print("Failed to extract valid JSON data from response")
                    save_to_excel(get_empty_gemini_row(journal_name, website_url),excel_name)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from response: {e}")
            
            
# here the function to save the text to a fil=======================================================================
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

def get_all_html_text(url):
    

    headers = header()
    headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    })

    try:
        # Set a timeout to avoid hanging indefinitely
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text(separator=' ', strip=True)
            # Limit the text content to 10,000 characters per link
            max_length = 10000
            if len(text_content) > max_length:
                print(f"Text content for {url} exceeds {max_length} characters, truncating.")
                text_content = text_content[:max_length]
            return {
                'text': text_content,
            }
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError as e:
        if isinstance(e.args[0], requests.packages.urllib3.exceptions.NewConnectionError) or "getaddrinfo failed" in str(e):
            print(f"Site can't be reached: {url}")
        else:
            print(f"Failed to connect to {url}. The website may be down or the URL might be invalid.")
        return None
    except requests.exceptions.Timeout:
        print(f"Request to {url} timed out. The server is taking too long to respond.")
        return None
    except requests.exceptions.TooManyRedirects:
        print(f"Too many redirects while trying to access {url}.")
        return None
    except requests.exceptions.RequestException as e:
        if "getaddrinfo failed" in str(e) or isinstance(e.__cause__, socket.gaierror):
            print(f"Site can't be reached: {url}")
        else:
            print(f"An error occurred while requesting {url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def save_text_to_file(text, filename, append=True, folder='downloaded_texts'):
    """Save the provided text to a text file in the specified folder."""
    try:
        # Create folder if it doesn't exist
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        # Ensure filename has .txt extension
        if not filename.endswith('.txt'):
            filename += '.txt'
            
        # Check if file exists and add incremental number if needed
        base_name = os.path.splitext(filename)[0]  # Get filename without extension
        extension = os.path.splitext(filename)[1]  # Get extension (.txt)
        counter = 1
        
        file_path = os.path.join(folder, filename)
        while os.path.exists(file_path):
            # If file exists and we're not appending, create a new filename
            filename = f"{base_name}_{counter}{extension}"
            file_path = os.path.join(folder, filename)
            counter += 1
        
        # Write text to file - use 'a' for append mode or 'w' for write mode
        mode = 'a' if append else 'w'
        with open(file_path, mode, encoding='utf-8') as f:
            for i, t in enumerate(text):
                if i > 0:  # Add separators between texts if needed
                    f.write("\n\n")
                f.write(t)
            
        action = "appended to" if append else "saved to"
        print(f"Text {action} {file_path}")

        return file_path
    
    except Exception as e:
        print(f"Error saving text to file: {e}")
        return None

def get_all_nav_links(url):
    print("flag1")
    headers = header()
    headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    })

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print("flag2")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            nav_links = []
            for a in soup.find_all('li'):
                a_tag = a.find('a')

                if a_tag and 'href' in a_tag.attrs:
                    href = a_tag['href']
                    # ...existing code...
                    if href.startswith('http'):
                        href = href
                    else:
                        if href.startswith('/'):
                            parsed_url = urlparse(url)
                            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                            href = base_url + href
                        elif not href.startswith(('http://', 'https://')):
                            parsed_url = urlparse(url)
                            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                            href = f"{base_url}/{href.lstrip('/')}"


                    # Skip unwanted links: pdf, images, gifs, videos, and certain keywords
                    skip_suffixes = [
                        '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp',
                        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.mp3', '.wav', '.ogg', '.webm'
                    ]
                    skip_keywords = ['login', 'signup', 'register', 'subscribe']
                    href_lower = href.lower()
                    if any(href_lower.endswith(suffix) for suffix in skip_suffixes) or any(keyword in href_lower for keyword in skip_keywords):
                        print(f"Skipping unwanted link: {href}")
                        continue

                    # Prevent duplicates
                    if href in [link['Website URL'] for link in nav_links]:
                        print(f"Skipping duplicate link: {href}")
                        continue
                    texts = (a_tag.text.strip() if a_tag else 'NONE')
                    print(f"Journal Name: {texts}, Website URL: {href}")
                    nav_links.append({
                        'Journal Name': texts,
                        'Website URL': href
                    })
            print("flag3")
            return nav_links[:30]
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while requesting {url}: {e}")
        print("flag4")
        return None

def fetch_journal_name_url_pairs(excel_file, name_col="Journal Name", url_col="Website URL", status_col="Status", number_col="numbers"):
    """
    Reads an Excel file and returns a list of dictionaries with Journal Name and URL,
    excluding rows where Status column equals "Done".
    Each dictionary has keys: 'Journal Name' and 'Website URL'.
    """
    df = pd.read_excel(excel_file)
    
    # Count skipped rows due to status before filtering
    skipped_count = 0
    if status_col in df.columns:
        skipped_count = df[df[status_col].fillna("").str.lower() == "done"].shape[0]
        print(f"Skipping {skipped_count} rows with status 'Done'")
    
    # Drop rows where either required column is missing
    df = df.dropna(subset=[name_col, url_col])
    
    # Filter out rows where Status is "Done"
    if status_col in df.columns:
        df = df[df[status_col].fillna("").str.lower() != "done"]
    
    # Build the list of dicts
    pairs = []
    for _, row in df.iterrows():
        pair = {name_col: row[name_col], url_col: row[url_col]}
        if number_col in df.columns and not pd.isna(row[number_col]):
            pair["number"] = row[number_col]
            print(f"Fetching website #{row[number_col]}: {row[name_col]}")
        pairs.append(pair)
    
    return pairs

def update_journal_status(excel_file, journal_name, status="Done", name_col="Journal Name", status_col="Status"):
    try:
        if not os.path.exists(excel_file):
            print(f"Excel file {excel_file} does not exist")
            return False

        df = pd.read_excel(excel_file)
        
        # Handle missing values in the name column before conversion
        df[name_col] = df[name_col].fillna("")
        
        # Normalize whitespace and case for matching
        df[name_col] = df[name_col].astype(str).str.strip()
        journal_name = str(journal_name).strip()

        if status_col not in df.columns:
            df[status_col] = ""

        df[status_col] = df[status_col].fillna("").astype(str)

        mask = df[name_col] == journal_name
        print(f"Looking for journal name: '{journal_name}'")
        print(f"Mask result: {mask}")
        print("Any match?", any(mask))

        if not any(mask):
            print(f"Journal '{journal_name}' not found in the Excel file")
            return False

        df.loc[mask, status_col] = status
        df.to_excel(excel_file, index=False)
        print(f"Updated status of '{journal_name}' to '{status}'")
        return True

    except Exception as e:
        print(f"Error updating journal status: {e}")
        return False

if __name__ == "__main__":


    # Example usage of the functions
    journal_list_excel = 'journal_list.xlsx'  # Path to your Excel file with journal names and URLs
    journal_data_excel = 'journal_data.xlsx'  # Path to save the journal data
  
    # Fetch journal name and URL pairs from the Excel file
    journal_list = fetch_journal_name_url_pairs(journal_list_excel)
    ten_only = journal_list[:300]  # Get only the first 10 entries
    max_nav = 30  # Set the maximum number of entries to process
    print(f"Total journals found: {len(ten_only)}")

    print("First 10 Journal Entries:")
    for journal in ten_only:
        print(f"Journal Name: {journal['Journal Name']}, Website URL: {journal['Website URL']}")

    # get all the links in the navigation bar

    for url in ten_only:
        journal_name = url['Journal Name']
        website_url = url['Website URL']

        print("\n\n")
        print(f"Processing: {journal_name} ({website_url})")
        nav_list = get_all_nav_links(website_url)
        texts = []

        if nav_list:
            print(f"Found {len(nav_list)} navigation links to process")      

        # Process each navigation link with proper rate limiting
        processed_urls = set()  # Track URLs we've already processed
        counter = 1

        if not nav_list:
            print("cannot find page or content is not journal related")
            save_text_to_file(['NONE'], journal_name, append=True, folder='downloaded_texts')
            save_json_to_excel(journal_name, website_url, excel_name=journal_data_excel, folder='downloaded_texts')
            update_journal_status(journal_list_excel, journal_name, status="Done", name_col="Journal Name", status_col="Status")
            continue
        
        nav_count = 0
        for i, nav in enumerate(nav_list):
            if nav_count >= max_nav:
                print(f"Reached maximum navigation links to process: {max_nav}")
                break
            nav_count += 1
            nav_url = nav['Website URL']
            
            # Skip if we've already processed this URL
            if nav_url in processed_urls:
                print(f"Skipping already processed URL: {nav_url}")
                continue
                
            print(f"\n[{i+1}/{len(nav_list)}] Processing: {nav['Journal Name']} ({nav_url})")
            
            delay = random.uniform(2, 5)
            print(f"Waiting {delay:.2f} seconds before next request...")
            time.sleep(delay)
            
            
            try:
                
                content = get_all_html_text(nav_url)
                # Add URL as context before the content for better organization
                if content and 'text' in content:
                    content_text = f"SOURCE URL: {nav_url}\n{content['text']}\n\n"
                    content['text'] = content_text
                texts.append(content['text'])
                processed_urls.add(nav_url)
                
                if content:
                    

                    print(f"Successfully retrieved content from {nav_url}")
                    # Process the content as needed
                    text_length = len(content['text']) if 'text' in content else 0
                    print(f"  - Text length: {text_length} characters")
                    
                else:
                    print(f"Failed to retrieve content from {nav_url}")
                
                # Implement exponential backoff for errors
                if i > 0 and i % 10 == 0:
                    longer_delay = random.uniform(10, 20)
                    print(f"Taking a longer break after 10 requests: {longer_delay:.2f} seconds")
                    time.sleep(longer_delay)
                    
            except Exception as e:
                print(f"Error processing {nav_url}: {e}")


            
            counter += 1
            

        save_text_to_file(texts, journal_name, append=True, folder='downloaded_texts')

        save_json_to_excel(journal_name, website_url, excel_name=journal_data_excel, folder='downloaded_texts')
        update_journal_status(journal_list_excel, journal_name, status="Done", name_col="Journal Name", status_col="Status")

        time.sleep(2)  # Short delay before processing the next URL