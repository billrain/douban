import requests
from bs4 import BeautifulSoup
import time
import random
import html
import re
from difflib import SequenceMatcher

def get_top_movies(url):
    try:
        # Create a session
        session = requests.Session()

        # Set up headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://movie.douban.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        # Send a GET request to the URL
        print(f"Sending request to {url}")
        response = session.get(url, headers=headers)
        response.raise_for_status()

        # Parse the HTML content
        print("Parsing HTML content")
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all movie items
        movie_items = soup.find_all('div', class_='item')
        print(f"Found {len(movie_items)} movie items")

        movies = []
        for i, item in enumerate(movie_items, 1):
            try:
                # Extract titles
                title_spans = item.find_all('span', class_='title')
                chinese_title = title_spans[0].text if title_spans else "N/A"
                english_title = title_spans[1].text.strip() if len(title_spans) > 1 else "N/A"

                # Remove the '/' character from the English title if present
                english_title = english_title[1:].strip() if english_title.startswith('/') else english_title

                # Extract rating
                rating_span = item.find('span', class_='rating_num')
                rating = rating_span.text if rating_span else "N/A"

                # Extract number of ratings
                votes_span = item.select_one('.star span:nth-of-type(4)')
                num_ratings = votes_span.text.strip('(人评价)') if votes_span else "N/A"

                # Extract Douban URL
                link = item.find('a')
                douban_url = link['href'] if link else "N/A"

                movies.append({
                    'chinese_title': chinese_title,
                    'english_title': english_title,
                    'rating': rating,
                    'num_ratings': num_ratings,
                    'douban_url': douban_url
                })
                print(f"Processed movie {i}: {chinese_title} / {english_title}")
            except Exception as e:
                print(f"Error processing movie {i}: {e}")

        return movies
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the page: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return []

def get_imdb_data():
    url = 'https://www.imdb.com/chart/top/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    imdb_data = {}
    movie_items = soup.find_all('li', class_='ipc-metadata-list-summary-item')
    
    for rank, item in enumerate(movie_items, 1):
        title = item.find('h3', class_='ipc-title__text').text.strip()
        title = re.sub(r'^\d+\.\s', '', title)  # Remove ranking number
        
        rating = item.find('span', class_='ipc-rating-star--imdb').text.strip()
        
        # Extract IMDb URL
        link = item.find('a', class_='ipc-title-link-wrapper')
        imdb_url = f"https://www.imdb.com{link['href']}" if link else "N/A"
        
        imdb_data[title.lower()] = {'rating': rating, 'rank': rank, 'url': imdb_url}
    
    return imdb_data

def find_best_match(title, imdb_data):
    # Remove any leading/trailing whitespace and convert to lowercase
    normalized_title = title.strip().lower()
    
    # Check for an exact match
    if normalized_title in imdb_data:
        return normalized_title
    
    # If no exact match is found, return None
    return None

# Fetch Douban Top 250 movies
base_url = 'https://movie.douban.com/top250'
all_movies = []

for page in range(3):
    url = f"{base_url}?start={page * 25}&filter="
    print(f"\nFetching Douban page {page + 1}...")
    
    page_movies = get_top_movies(url)
    all_movies.extend(page_movies)
    
    if page < 9:
        delay = random.uniform(3, 5)
        print(f"Waiting for {delay:.2f} seconds before the next request...")
        time.sleep(delay)

# Fetch IMDb Top 250 movies
print("\nFetching IMDb Top 250 movies...")
imdb_data = get_imdb_data()
print(f"Number of IMDb movies fetched: {len(imdb_data)}")
print("Sample IMDb data:")
for title, data in list(imdb_data.items())[:5]:
    print(f"{title}: {data}")

# Generate HTML
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Douban Top 250 Movies with IMDb Ratings</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f0f4f8;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 40px;
            font-size: 2.8em;
            font-weight: 600;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            background-color: #fff;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            border-radius: 12px;
            overflow: hidden;
        }
        th, td {
            padding: 18px 15px;
            text-align: left;
        }
        th {
            background-color: #34495e;
            color: #fff;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        th:hover {
            background-color: #2c3e50;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        tr:hover {
            background-color: #e8f4f8;
        }
        th.sort-asc::after {
            content: " ▲";
            font-size: 0.8em;
        }
        th.sort-desc::after {
            content: " ▼";
            font-size: 0.8em;
        }
        a {
            color: #3498db;
            text-decoration: none;
            transition: color 0.3s;
        }
        a:hover {
            color: #2980b9;
            text-decoration: underline;
        }
        .rank {
            font-weight: 600;
            color: #2c3e50;
        }
        .rating {
            font-weight: 600;
            color: #f39c12;
        }
        .movie-title {
            font-weight: 600;
            color: #34495e;
        }
        @media (max-width: 768px) {
            table {
                font-size: 14px;
            }
            th, td {
                padding: 12px 10px;
            }
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tablesort/5.2.1/tablesort.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>Douban Top 250 Movies with IMDb Ratings</h1>
        <table id="movie-table">
            <thead>
                <tr>
                    <th data-sort-method="number">Douban Rank</th>
                    <th>Chinese Title</th>
                    <th>English Title</th>
                    <th data-sort-method="custom-number">Douban Rating</th>
                    <th data-sort-method="custom-number">Douban Ratings</th>
                    <th data-sort-method="custom-number">IMDb Rating</th>
                    <th data-sort-method="custom-number">IMDb Rank</th>
                </tr>
            </thead>
            <tbody>
"""

for i, movie in enumerate(all_movies, 1):
    best_match = find_best_match(movie['english_title'], imdb_data)
    imdb_info = imdb_data.get(best_match, {'rating': 'N/A', 'rank': 'N/A', 'url': '#'}) if best_match else {'rating': 'N/A', 'rank': 'N/A', 'url': '#'}
    html_content += f"""
        <tr>
            <td class="rank">{i}</td>
            <td class="movie-title"><a href="{html.escape(movie['douban_url'])}" target="_blank">{html.escape(movie['chinese_title'])}</a></td>
            <td>{html.escape(movie['english_title'])}</td>
            <td class="rating">{movie['rating']}</td>
            <td>{movie['num_ratings']}</td>
            <td class="rating">{imdb_info['rating']}</td>
            <td><a href="{html.escape(imdb_info['url'])}" target="_blank">{imdb_info['rank']}</a></td>
        </tr>
    """

html_content += """
            </tbody>
        </table>
    </div>
    <script>
        Tablesort.extend('custom-number', function(item) {
            return item !== 'N/A';
        }, function(a, b) {
            a = a === 'N/A' ? Infinity : parseFloat(a);
            b = b === 'N/A' ? Infinity : parseFloat(b);
            return a - b;
        });

        new Tablesort(document.getElementById('movie-table'));
    </script>
</body>
</html>
"""

# Write the HTML content to a file
with open('douban_imdb_top_250_movies.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\nTotal movies fetched: {len(all_movies)}")
print("HTML file 'douban_imdb_top_250_movies.html' has been created.")