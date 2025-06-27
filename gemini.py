import os
import json
import re
import pandas as pd
from google import genai
from google.genai import types
import dotenv
from dotenv import load_dotenv
from PIL import Image # Import Pillow

load_dotenv()


# def is_valid_image(file_path):
#     """Checks if a file is a valid image using Pillow."""
#     try:
#         with Image.open(file_path) as img:
#             img.verify() # Verify the image data
#         return True
#     except (IOError, SyntaxError, Image.UnidentifiedImageError) as e:
#         print(f"Invalid or corrupted image found: {file_path} - {e}")
#         return False
#     except Exception as e:
#         print(f"Unexpected error checking image {file_path}: {e}")
#         return False

# def get_images_from_folder(folder_path='downloaded_images', max_images=50): # Reduced max_images for safety
#     """Get a list of valid image files from the folder, limited to max_images."""
#     images = []
#     if not os.path.exists(folder_path):
#         print(f"Image folder '{folder_path}' does not exist.")
#         return images
    
#     valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
#     count = 0
    
#     for filename in os.listdir(folder_path):
#         if count >= max_images:
#             break
            
#         file_path = os.path.join(folder_path, filename)
#         ext = os.path.splitext(filename)[1].lower()
        
#         if os.path.isfile(file_path) and ext in valid_extensions:
#             if is_valid_image(file_path): # Use the new validation function
#                 # Optional: Check file size before adding, to warn about large files
#                 file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
#                 if file_size_mb > 7:
#                     print(f"Warning: Image {filename} is {file_size_mb:.2f}MB, exceeding 7MB inline limit. It might fail.")
                
#                 images.append(file_path)
#                 count += 1
#                 print(f"Added image: {filename}")
#             else:
#                 print(f"Skipping invalid image: {filename}")
    
#     print(f"Found {len(images)} valid images out of {max_images} requested.")
#     return images


def generate(text):
    """Generate content using only text (no images)"""
    client = genai.Client(
        api_key=os.environ.get("GeminiKey"),
    )

    prompt_part1 = f"""
    You are an expert AI Journal Scraper and Data Extractor. Your task is to analyze the provided text from a journal's website and extract specific information about it.

Your goal is to fill in the details for the following fields. For fields with predefined choices, you MUST select one of the provided options. If information for a field is not explicitly found or cannot be confidently inferred from the text, mark its value as \"Unknown\" or \"Not Applicable\" where specified.

Present the extracted information in a structured JSON format.

---

**
{text}
**

---

**Extraction Fields and Rules:**
"""

    json_template = """```json
{
  "Journal Name": "...",
  "Publisher Name": "...",
  "ISSN": "...",
  "Website URL": "...",
  "Editorial Board Members": "...",
  "Peer Review Process": "...",
  "Publishing Model": "...",
  "Publication Fees/Article Processing Fees": "...",
  "Publication Frequency": "...",
  "DOI Availability": "...",
  "Indexing": [
    "..."
  ],
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
}```"""

    extraction_rules = """
1.  **Journal Name:** The full name of the journal.
2.  **Publisher Name:** The name of the organization that publishes the journal.
3.  **ISSN:** The International Standard Serial Number (can be print ISSN, online ISSN, or both).
4.  **Website URL:** The primary URL of the journal's website (this should be the URL the input text came from).
5.  **Editorial Board Members:** (Listed, Unknown) - Is a list of editorial board members explicitly available and clearly presented if yes then put listed else put unknown?
6.  **Peer Review Process:** (Single Blind, Double Blind, Open Peer Review, Unknown) - How does the journal describe its peer review process?
7.  **Publishing Model:** (Open Access, Subscription, Unknown) - How does the journal make its content available?
8.  **Publication Fees/Article Processing Fees:** The amount or range of fees charged to authors. If \"No fees,\" state \"0\". If present but specific amount unknown, state \"-1\". If not mentioned, state \"-1\".
9.  **Publication Frequency:** (Weekly, Monthly, Twice a month, Quarterly, Twice every quarter, Yearly, Twice a year, 3 times a year, Unknown) - How often does the journal publish new issues?
10. **DOI Availability:** (Yes, No, Unknown) - Does the journal explicitly mention assigning DOIs (Digital Object Identifiers) to its articles?
11. **Indexing:** (Scopus, Web of Science, DOAJ, Google, Others, Unknown) - put only 1 prioritize the order given explicitly mentioned indexing services. If \"Others\" is chosen state \"Others\", state \"Unknown\".
12. **Editorial Process Transparency:** (Listed, Unknown) - Is the editorial process (beyond peer review) clearly described and transparently presented on the website?
13. **Journal's Scope & Aims:** (Domain-specific, Multi-disciplinary, Broad, Unknown) - Select the journal's stated scope and aims from the following options: Domain-specific, Multi-disciplinary, Broad, Unknown.
14. **Calls for Papers (CFPs):** (Weekly, Monthly, Twice a Month, Quarterly, Twice every Quarter, Yearly, Twice a Year, 3 Times a Year, Unknown) - How often does the journal issue calls for papers?
15. **Year Established:** The year the journal was founded or first published.
16. **Journal's Acceptance Rate:** The stated acceptance rate (e.g., \"30%\"). If not stated, \"Unknown\".
17. **Publication Days:** The typical number of days from submission to publication. If not stated or cannot be confidently inferred, \"Unknown\".
18. **Cite Score:** The journal's stated CiteScore. If not stated, \"Unknown\".
19. **Impact Factor:** find the journal's stated Impact Factor, \"Unknown\".
20. **Include Author Guidelines:** (Yes, No, Unknown) - Are clear guidelines for authors explicitly provided on the website?
21. **Submission Process:** (System, Email, Unknown) - How do authors submit their manuscripts? (e.g., through an online submission system, via email).
22. **Publication Ethics:** (Listed, Unknown) - Does the journal have a clearly stated section on publication ethics or adherence to ethical guidelines (e.g., COPE)?
23. **University Affiliation:** (Yes, No, Unknown) - Does the journal claim or show a clear affiliation with a university?
24. **Name of University:** (If \"University Affiliation\" is \"Yes\", state the full name of the university. Otherwise, put \"NONE\").

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
            print(chunk.text, end="")
            full_response += chunk.text
    except Exception as e:
        print(f"\nError during Gemini API call: {e}")

    return full_response


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

def save_to_excel(json_data, output_file="journal_data.xlsx"):
    """Save the extracted JSON data to an Excel file, appending if file exists."""
    try:
        if "Indexing" in json_data and isinstance(json_data["Indexing"], list):
            json_data["Indexing"] = ", ".join(json_data["Indexing"])

        new_df = pd.DataFrame([json_data])

        if os.path.exists(output_file):
            # Read existing data
            try:
                existing_df = pd.read_excel(output_file)
                # Append new data
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


def is_text_empty_or_none(text):
    """
    Returns True if the text is empty, contains only whitespace, or contains 'NONE' (case-insensitive).
    Otherwise, returns False.
    """
    if not text or str(text).strip() == "" or str(text).strip().upper() == "NONE":
        return True
    return False


def get_text_from_folder(folder_path = 'downloaded_texts', file_name='Name of the Journal'):
    
    specific_file = file_name  # Replace with your specific file name
    

    file_path = os.path.join(folder_path, specific_file)
    if os.path.exists(file_path) and file_path.endswith(".txt"):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text_content = file.read()
            print(f"Processing file: {specific_file}")
        except Exception as e:
            print(f"Error reading file {specific_file}: {e}")
            text_content = ""
    else:
        print(f"File not found or not a text file: {specific_file}")
        text_content = ""

def save_text_to_file( file_name, append=False, folder='downloaded_texts'):
    text_content = get_text_from_folder(folder, file_name=file_name)

    if is_text_empty_or_none(text_content):
        print("Text is empty or contains NONE")
        # Save a blank row with correct defaults
        save_to_excel(get_empty_gemini_row("NONE", "NONE"))
    else:
        response = generate(text_content)
        json_data = extract_json_from_response(response)
        
        if json_data:
            save_to_excel(json_data)
        else:
            print("Failed to extract valid JSON data from response")

# Main execution
if __name__ == "__main__":
    
    save_text_to_file('Academic Research Reviews', append=True, folder='downloaded_texts')
    