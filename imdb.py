import requests
from bs4 import BeautifulSoup
import random
import time

def fetch_imdb_top_250():
    base_url = "https://www.imdb.com/chart/top/?ref_=tt_awd"
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    movie_list = []
    
    try:
        for start in range(1, 251, 50):
            url = f"{base_url}?start={start}&ref_=tt_awd_top_250"
            print(f"Fetching movies {start} to {start+49}...")
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            movies = soup.find_all('li', class_='ipc-metadata-list-summary-item')
            
            for movie in movies:
                title_elem = movie.find('h3', class_='ipc-title__text')
                year_elem = movie.find('span', class_='cli-title-metadata-item')
                rating_elem = movie.find('span', class_='ipc-rating-star--imdb')
                
                if title_elem and year_elem and rating_elem:
                    title = title_elem.text.strip()
                    year = year_elem.text.strip()
                    rating = rating_elem.text.strip()
                    
                    movie_list.append({
                        'title': title,
                        'year': year,
                        'rating': rating
                    })
                else:
                    print(f"Couldn't find all elements for a movie. HTML: {movie}")
            
            # Add a delay between requests
            time.sleep(random.uniform(5, 7))
        
        return movie_list
    except requests.RequestException as e:
        print(f"An error occurred while fetching the page: {e}")
        return None

# Fetch and print the movie list
movies = fetch_imdb_top_250()
if movies:
    for i, movie in enumerate(movies, 1):
        print(f"{i}. {movie['title']} ({movie['year']}) - Rating: {movie['rating']}")
    print(f"Total movies fetched: {len(movies)}")
else:
    print("Failed to fetch movies.")