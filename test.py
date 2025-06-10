import requests
from bs4 import BeautifulSoup
import random
import urllib.parse

def search_linkedin_profiles(name, max_results=3):
    # Broader query to catch variations
    query = f'site:linkedin.com/posts/ {name}'
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.bing.com/search?q={encoded_query}"
    print(url)
    headers_list = [
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"},
        {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"},
    ]
    
    headers = random.choice(headers_list)

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    results = []
    for item in soup.find_all('li', {'class': 'b_algo'}):
        link = item.find('a')
        if link and 'linkedin.com/in/Jaydee' in link['href']:
            profile_url = link['href']
            if profile_url not in results:
                results.append(profile_url)
        if len(results) >= max_results:
            break
    return results

# Try "Jaydee C. Ballaho" or "Ballaho"
profiles = search_linkedin_profiles("Jaydee Ballaho")

if profiles:
    print("Found LinkedIn Profiles:")
    for i, url in enumerate(profiles, 1):
        print(f"{i}. {url}")
else:
    print("No LinkedIn profiles found.")