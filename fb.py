import requests
from bs4 import BeautifulSoup
import random
import time

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

def search_facebook_profile(name, school):
    query = f'{name} site:facebook.com'
    url = f'https://html.bing.com/html/?q={query}'

    headers = header()
    # Add more headers to appear more like a browser
    headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    })
    
    print(f"Using headers: {headers}")
    
    # Add a delay to mimic human behavior
    time.sleep(random.uniform(1, 3))

    try:
        session = requests.Session()  # Use a session to maintain cookies
        response = session.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example usage
profiles = search_facebook_profile("Azief Saclolo", "Western Mindanao State University")

print("Facebook profiles found:")
if not profiles:
    print("No profiles found.")
else:
    for profile in profiles:
        print(profile)