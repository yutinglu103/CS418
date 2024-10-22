import unittest
from hw1part2 import *

class TestHW1Part2(unittest.TestCase):
	"""
	Part2: Web scraping and data collection
	"""

	def test_spotify_search_params(self):
		"spotify_search_params: Correct implementation"
		client_id = "b0e357c92a534fbbb8c8fa3a3c924213"
		client_secret = "28bbb0f189c04564b41852f71eaaaee1"
		artist = "Taylor Swift"
		url, headers, params = spotify_search_params(client_id, client_secret,artist=artist, track="Lover", type="track", limit=5)
		expected_url = 'https://api.spotify.com/v1/search'
		self.assertTrue(url == expected_url, msg="API URL does not match")
		self.assertTrue(params.get("limit") == 5, "Keyword args not included in url params")
		self.assertTrue(params.get("q") == 'artist:Taylor Swift track:Lover', msg="Not corret query in API request")
		# Add more tests

	def test_spotify_search(self):
		"spotify_search: Correct implementation"
		client_id = "b0e357c92a534fbbb8c8fa3a3c924213"
		client_secret = "28bbb0f189c04564b41852f71eaaaee1"
		artist = "Taylor Swift"
		total, tracks = spotify_search(client_id, client_secret,artist=artist, track="Lover", type="track", limit=5)
		self.assertTrue(total == 44, msg="Incorrect number of searched tracks")
		
	def paginated_spotify_search_requests(self):
		"paginated_spotify_search_requests: Correct implementation"
		client_id = "b0e357c92a534fbbb8c8fa3a3c924213"
		client_secret = "28bbb0f189c04564b41852f71eaaaee1"
		artist = "Taylor Swift"
		total = 200
		limit = 50
		all_track_requests = paginated_spotify_search_requests(client_id, client_secret, artist, total, limit)
		self.assertTrue(len(all_track_requests) == 4, msg="Incorrect number of pages")
		# offsets = [0, 50, 100, 150]
		for i, request in enumerate(all_track_requests):
			self.assertTrue(request[0] == "https://api.spotify.com/v1/search", msg="API URL does not match")
			self.assertTrue(request[2].get("type") == "track", msg="Missing or invalid url parameter")
		# Add more tests

	# You can add other test cases








