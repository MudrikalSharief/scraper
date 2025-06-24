from bs4 import BeautifulSoup
import random
import requests
import os
import time
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

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

def is_allowed_by_robots(url):
    """Check if the URL is allowed by robots.txt"""
    try:
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.read()
        
        return parser.can_fetch("*", url)
    except Exception as e:
        print(f"Error checking robots.txt: {e}")
        return True  # Default to allowing in case of error
    
def download_image(img_url, folder='downloaded_images'):
    try:
        # Create folder if it doesn't exist
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        # Extract filename from URL
        filename = os.path.basename(urlparse(img_url).path)
        if not filename:
            filename = f"image_{hash(img_url)}.jpg"
            
        # Download the image
        img_response = requests.get(img_url, stream=True)
        if img_response.status_code == 200:
            file_path = os.path.join(folder, filename)
            with open(file_path, 'wb') as f:
                for chunk in img_response.iter_content(1024):
                    f.write(chunk)
            return file_path
        else:
            print(f"Failed to download image: {img_url}")
            return None
        
    except Exception as e:
        print(f"Error downloading image {img_url}: {e}")
        return None

def get_image_urls(soup):
    images = []
    # Find all image tags and extract their URLs and alt text
    if not soup:
        print("No soup object provided.")
        return images
    
    for img in soup.find_all('img'):
        img_url = img.get('src')

        if img_url in images:
            print(f"Skipping duplicate image URL: {img_url}")
            continue

        if img_url:
            # Handle relative URLs
            if img_url.startswith('/'):
                img_url = url.rstrip('/') + img_url
            # Handle protocol-relative URLs
            elif img_url.startswith('//'):
                img_url = 'https:' + img_url
            
            img_alt = img.get('alt', '')
            images.append({'url': img_url, 'alt': img_alt})
    
    return images

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
            text_content =  soup.get_text(separator=' ', strip=True)

            #get all images from the website
            
            images = get_image_urls(soup)
            if not images:
                print("No images found on the page.")
                images = []
            
            return {
                'text': text_content,
                'images': images
            }
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"Failed to connect to {url}. The website may be down or the URL might be invalid.")
        return None
    except requests.exceptions.Timeout:
        print(f"Request to {url} timed out. The server is taking too long to respond.")
        return None
    except requests.exceptions.TooManyRedirects:
        print(f"Too many redirects while trying to access {url}.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while requesting {url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def save_text_to_file(text, filename, append=False, folder='downloaded_texts'):
    """Save the provided text to a text file in the specified folder."""
    try:
        # Create folder if it doesn't exist
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        # Ensure filename has .txt extension
        if not filename.endswith('.txt'):
            filename += '.txt'
            
        file_path = os.path.join(folder, filename)
        
        # Write text to file - use 'a' for append mode or 'w' for write mode
        mode = 'a' if append else 'w'
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(text)
            
        action = "appended to" if append else "saved to"
        print(f"Text {action} {file_path}")
        return file_path
    
    except Exception as e:
        print(f"Error saving text to file: {e}")
        return None

def get_all_nav_links(url):
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
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            nav_links = []
            for a in soup.find_all('li'):
                a_tag = a.find('a')

                if a_tag and 'href' in a_tag.attrs:
                    href = a_tag['href']
                    
                    if href.startswith('http'):
                        # If the link is absolute, use it as is
                        href = href
                    else:
                        # Handle relative URLs
                        if href.startswith('/'):
                            # Remove trailing slash from base URL if the href already has a leading slash
                            parsed_url = urlparse(url)
                            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                            href = base_url + href
                        elif not href.startswith(('http://', 'https://')):
                            # Handle relative paths without leading slash
                            parsed_url = urlparse(url)
                            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                            href = f"{base_url}/{href.lstrip('/')}"
                            
                    if href in nav_links:
                        print(f"Skipping duplicate link: {href}")
                        continue
                    texts = (a_tag.text.strip() if a_tag else 'NONE')
                    # Append the link and its text to the list
                    print(f"Journal Name: {texts}, Website URL: {href}")
                    nav_links.append({
                    'Journal Name': texts,
                    'Website URL': href
                    })

            return nav_links
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while requesting {url}: {e}")
        return None



# get all the links in the navigation bar
url = "http://aocrj.org/"    
nav_list = get_all_nav_links(url)
texts = []

if nav_list:
    print(f"Found {len(nav_list)} navigation links to process")      

# Process each navigation link with proper rate limiting
processed_urls = set()  # Track URLs we've already processed

for i, nav in enumerate(nav_list):
    nav_url = nav['Website URL']
    
    # Skip if we've already processed this URL
    if nav_url in processed_urls:
        print(f"Skipping already processed URL: {nav_url}")
        continue
        
    print(f"\n[{i+1}/{len(nav_list)}] Processing: {nav['Journal Name']} ({nav_url})")
    
    # Check robots.txt before scraping
    if not is_allowed_by_robots(nav_url):
        print(f"Skipping {nav_url} (disallowed by robots.txt)")
        continue
    
    # Add random delay between requests (2-5 seconds)
    delay = random.uniform(2, 5)
    print(f"Waiting {delay:.2f} seconds before next request...")
    time.sleep(delay)
    
    # Get content from the navigation URL (not the original URL)
    try:
        
        content = get_all_html_text(nav_url)
        texts.append(content['text'] if content and 'text' in content else '')
        processed_urls.add(nav_url)
        
        if content:
            save_text_to_file(content['text'], ''.join(nav_url.split('/')[2:]))

            print(f"Successfully retrieved content from {nav_url}")
            # Process the content as needed
            text_length = len(content['text']) if 'text' in content else 0
            image_count = len(content['images']) if 'images' in content else 0
            print(f"  - Text length: {text_length} characters")
            print(f"  - Images found: {image_count}")
            
            # Optional: Download images with additional delays
            if 'images' in content and content['images']:
                print(f"  - Would download {len(content['images'])} images ")
            # Download images 
                for img in content['images']:  
                    img_url = img['url']
                    saved_path = download_image(img_url)
                    if saved_path:
                        print(f" Downloaded: {img_url}")
                    time.sleep(1)  # 1 second between image downloads
        else:
            print(f"Failed to retrieve content from {nav_url}")
        
        # Implement exponential backoff for errors
        if i > 0 and i % 10 == 0:
            longer_delay = random.uniform(10, 20)
            print(f"Taking a longer break after 10 requests: {longer_delay:.2f} seconds")
            time.sleep(longer_delay)
            
    except Exception as e:
        print(f"Error processing {nav_url}: {e}")

    break  # Remove this break to process all links