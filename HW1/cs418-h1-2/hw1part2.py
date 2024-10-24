import io, time, json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

import base64

client_id = "b0e357c92a534fbbb8c8fa3a3c924213"
client_secret = "28bbb0f189c04564b41852f71eaaaee1"

# 2% credit
def retrieve_html(url):
    """
    Return the raw HTML at the specified URL.

    Args:
        url (string): 

    Returns:
        status_code (integer):
        raw_html (string): the raw HTML content of the response, properly encoded according to the HTTP headers.
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    html_content = response.text
    return html_content

#3% credit
def parse_imdb(imdb_data):
    """
    Return the movie lists from imdb top chart URL.

    Args:
        raw_html (string): 

    Returns:
        movies (list): the list of movies with Title, Description and Rating.
    
        Example:
        movies = [
        {
            'Title': 'The Shawshank Redemption',
            'Description': 'A Maine banker convicted of the murder of his wife and her lover...',
            'Rating': 9.3,
        },
        {
            'Title': 'The Godfather',
            'Description': 'Don Vito Corleone, head of a mafia family, decides to hand over his empire...',
            'Rating': 9.2,

        },
            # ... more
        ]

    
    """
    soup = BeautifulSoup(imdb_data, 'html.parser')
    json_ld_script = soup.find('script', type='application/ld+json')
    json_data = json_ld_script.string
    data = json.loads(json_data)
    movies = []
    for item in data['itemListElement']:
       movie = item['item']
       title = movie['name']
       description = movie['description']
       aggregateRating = movie['aggregateRating']
       rating = aggregateRating['ratingValue']
       movies.append({
            'Title': title,
            'Description': description,
            'Rating' : rating
        })
       
    return  movies

# 1% credit
def read_api_key(filepath):
    """
    Read the Spotify API Keys from file.
    
    Args:
        filepath (string): File containing API Keys
    Returns:
        client_id (string): Your client id
        client_secret (string): Your client secret
    """
    
    # feel free to modify this function if you are storing the API Key differently
    with open(filepath, 'r') as file:
       credentials = json.load(file)
    
    # Extract the credentials
    client_id = credentials['client_id']
    client_secret = credentials['client_secret']
    return client_id, client_secret


# 2% credit
def access_spotify(client_id, client_secret):
    """
    Authenticates the user and retrieves the bearer token required for API requests.
    """
    client_id = "b0e357c92a534fbbb8c8fa3a3c924213"
    client_secret = "28bbb0f189c04564b41852f71eaaaee1"

    auth_url = 'https://accounts.spotify.com/api/token'
    auth_string = f"{client_id}:{client_secret}"
    
    auth_bytes = auth_string.encode('ascii')
    auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
    auth_header = auth_base64

    headers = {
        'Authorization': f'Basic {auth_header}',
        'user-agent':'my-app/0.01'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    
    response = requests.post(auth_url, headers=headers, data=data)
    token_info = response.json()
    access_token = token_info['access_token']
    return access_token

# 4% credit    
def spotify_search_params(client_id, client_secret, **kwargs):
    """
    Construct url, headers and params. Reference API docs (link above) to use the arguments
    """
    client_id = "b0e357c92a534fbbb8c8fa3a3c924213"
    client_secret = "28bbb0f189c04564b41852f71eaaaee1"
    # What is the url endpoint for search?
    url = "https://api.spotify.com/v1/search"
    # How is Authentication performed? Hint: use access_token from function of access_spotify
    access_token = access_spotify(client_id, client_secret)
    headers = headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    # SPACES in url is problematic. How should you handle queries with field filters?
    query_params = []
    for key, value in kwargs.items():
        if key in ['artist', 'track', 'album']:
            query_params.append(f'{key}:{value}')
    # Combine all query parameters into the 'q' field
    query = ' '.join(query_params)
    
    # Include keyword arguments in params dictionary
    params = {
        'q': query,
        'type': kwargs.get("type", "track"),  # Default search type is track
        'limit': kwargs.get("limit", 10),  # Limit results, default is 10
        'offset': kwargs.get("offset", 0), 
    }
    
    return url, headers, params


# 2% credit
def api_get_request(url, headers, params):
    """
    Send a HTTP GET request and return a json response 
    
    Args:
        url (string): API endpoint url
        headers (dict): A python dictionary containing HTTP headers including Authentication to be sent
        url_params (dict): The parameters (required and optional) supported by endpoint
        
    Returns:
        results (json): response as json
    """
    # See requests.request?
    response = requests.get(url, headers=headers, params=params)
    return response.json()
    

def spotify_search(client_id, client_secret, **kwargs):
    """
    Make an authenticated request to the Spotify API and return search results.

    Args:
        client_id (string): Your Spotify Client ID for Authentication
        client_secret (string): Your Spotify Client Secret for Authentication
        **kwargs: Additional search parameters (e.g., artist, track, album, etc.)

    Returns:
        total (integer): Total number of tracks matching the query
        tracks (list): List of dicts representing each track with name, and popularity
    """
    client_id = "b0e357c92a534fbbb8c8fa3a3c924213"
    client_secret = "28bbb0f189c04564b41852f71eaaaee1"

    url, headers, params = spotify_search_params(client_id, client_secret, **kwargs)
    response_json = api_get_request(url, headers, params)
    total = response_json['tracks']['total']
    tracks = []
    if response_json['tracks']['items']:
            popularities = []
            for track in response_json['tracks']['items']:
                track_info = {
                    'track_name': track['name'],
                    'popularity': track['popularity']
                }
                tracks.append(track_info)
                popularities.append(track['popularity'])
            
    return total, tracks

# 4% credit
def paginated_spotify_search_requests(client_id, client_secret, artist_name, total,limit):
    """
    Returns a list of tuples (url, headers, params) for paginated search of all restaurants
    Args:
        client_id, client_secret (string): Your Spotify API Key for Authentication
        artist_name (string): Artist name
        total (int): Total number of items to be fetched
        limit (int): Number of items to fetch per request (default is 50)
    Returns:
        results (list): list of tuple (url, headers, params)
    """
    # HINT: Use total, offset and limit for pagination
    # You can reuse function location_search_params(...)
    client_id = "b0e357c92a534fbbb8c8fa3a3c924213"
    client_secret = "28bbb0f189c04564b41852f71eaaaee1"

    results = []
    num_pages = (total + limit - 1) // limit
    for page in range(num_pages):
        # Calculate the offset for the current page
        offset = page * limit
        # Generate the URL, headers, and params for this request
        url, headers, params = spotify_search_params(client_id, client_secret,artist=artist_name,limit=limit,offset=offset)
        
        # Append the request details to the list
        results.append((url, headers, params))
    
    return results


# 3% credit
def get_tracks(client_id, client_secret, artist_name):
    """
    Construct the pagination requests for ALL tracks by Given Artist on Spotify.

    Args:
        client_id (string): Your Spotify Client ID for Authentication
        client_secret (string): Your Spotify Client Secret for Authentication
        artist_name (string): Artist name

    Returns:
        results (list): List of dicts representing each track
    """
    client_id = "b0e357c92a534fbbb8c8fa3a3c924213"
    client_secret = "28bbb0f189c04564b41852f71eaaaee1"

    total_items = 300
    limit = 50
    
    tracks_request = paginated_spotify_search_requests(client_id, client_secret,artist_name, total_items,limit)
    
    # Use returned list of (url, headers, url_params) and function api_get_request to retrive all restaurants
    # REMEMBER to pause slightly after each request.
    result = []

    for url, headers, params in tracks_request:
        response_json = api_get_request(url, headers, params)
        
        if 'tracks' in response_json and 'items' in response_json['tracks']:
            for track in response_json['tracks']['items']:
                album = track['album']
                track_info = {
                    'track_name': track['name'],
                    'album_name': album['name'],
                    'popularity': track['popularity']
                }
                result.append(track_info)
        
        # Pause to respect rate limits
        time.sleep(0.5)  # Sleep for 200 milliseconds  
    return result

# 4% credit
def parse_api_response(data):
    """
    Parse Spotify API results to extract cover images URLs.
    
    Args:
        data (string): String of properly formatted JSON.

    Returns:
        (list): list of URLs as strings from the input JSON.
    """
    
    all_image_urls = []

    for track in data['tracks']['items']:
        if 'album' in track and 'images' in track['album']:
            for image in track['album']['images']:
                all_image_urls.append(image['url'])

    return all_image_urls


# 4% credit
def fetch_html(url):
    """
    Fetch the HTML content of the specified URL.

    Args:
        url (string): The URL of the IMDb page.

    Returns:
        response_text (string): The raw HTML content of the page.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch page: {response.status_code}")


def parse_page(html):
    """
    Parse reviews from an IMDb movie reviews page.

    Args:
        html (string): HTML content of the IMDb reviews page.

    Returns:
        reviews (list): A list of dictionaries, each containing the review's rating, author, date, and content.
    """
    soup = BeautifulSoup(html,'html.parser')
    reviews_list = []

    soup = BeautifulSoup(html,'html.parser')
    reviews_list = []

    # Find all review containers on the page
    review_containers = soup.find_all('div', class_='lister-item-content')
    # HINT: print reviews to see what http tag to extract

    for review_container in review_containers:
        rating_tag = review_container.find('span', class_='rating-other-user-rating')
        rating = int(rating_tag.find('span').text) if rating_tag else None
        author = review_container.find('span', class_='display-name-link').text.strip()
        review_date = review_container.find('span', class_='review-date').text.strip()
        content = review_container.find('div', class_='text').text.strip()

        review = {
            'rating': rating,
            'Author': author,
            'review_date': review_date,
            'review_content': content
        }
        reviews_list.append(review)
    
    return reviews_list

def get_ajax_url_and_key(html):
    soup = BeautifulSoup(html, 'html.parser')
    load_more_button = soup.find('div', class_='load-more-data')
    
    if load_more_button:
        ajax_url = "https://www.imdb.com" + load_more_button['data-ajaxurl']
        pagination_key = load_more_button['data-key']
        return ajax_url, pagination_key
    else:
        return None, None
    
def html_fetcher(url):
    """
    Fetch the HTML content and status code from the specified URL.

    Args:
        url (string): The URL of the webpage.

    Returns:
        (int, string): A tuple containing the status code and the raw HTML content of the page.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    return response.status_code, response.text
    

def fetch_ajax_page(ajax_url, pagination_key=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    params = {'ref_': 'undefined'}
    if pagination_key:
        params['paginationKey'] = pagination_key
    response = requests.get(ajax_url, headers=headers, params=params)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        new_pagination_key = soup.find('div', {'data-key': True})
        new_pagination_key = new_pagination_key['data-key'] if new_pagination_key else None
        return new_pagination_key, response.text
    else:
        raise Exception(f"Failed to fetch AJAX page: {response.status_code}")

# 4% credits
def all_reviews(url):
    """
    Retrieve ALL of the reviews for a single restaurant on Yelp.

    Parameters:
        url (string): Yelp URL corresponding to the restaurant of interest.
        html_fetcher (function): A function that takes url and returns html status code and content
    
    Returns:
        reviews (list): list of dictionaries containing extracted review information
    """
    all_reviews = []
    code, initial_html = html_fetcher(url)
    ajax_url, pagination_key = get_ajax_url_and_key(initial_html)
    
    '''if not ajax_url or not pagination_key:
        raise Exception("Failed to find the AJAX URL or pagination key for loading more reviews.")'''
    
    while True:
        pagination_key, html = fetch_ajax_page(ajax_url, pagination_key)
        reviews = parse_page(html)
        all_reviews.extend(reviews)
        
        if not pagination_key:
            break

    return all_reviews