from bs4 import BeautifulSoup
import json

def _get_var_init_data(soup: BeautifulSoup):
	index = -1
	for i, item in enumerate(soup.find_all('script')):
		if item.text.startswith('var ytInitialData'):
			index = i
	return soup.find_all('script')[index].text[20:-1] if index != -1 else ''
		
class StreamInfo:
	"""
	Class to format a streams's information.
	NOTE: The given stream_id is assumed to be live, but should work with waiting rooms.
	"""
	def __init__(self, stream_id: str, request: str):
		self.id = stream_id
		self.url = f'https://youtu.be/{stream_id}'
		soup = BeautifulSoup(request, 'lxml')
		self.__find_metadata(soup)

	def __find_metadata(self, soup):
		self.title = soup.find(itemprop='name')['content']
		self.thumbnail = soup.find(itemprop='thumbnailUrl')['href']

		author_tag = soup.find(itemprop='author').contents
		self.author = author_tag[1]['content']
		self.author_url = author_tag[0]['href']

		initial_data = json.loads(_get_var_init_data(soup))
		author_bar = initial_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]
		author_bar = author_bar['videoSecondaryInfoRenderer']['owner']['videoOwnerRenderer']
		self.author_id = author_bar['title']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId']
		self.author_icon = author_bar['thumbnail']['thumbnails'][0]['url'].split('=s')[0]

	def __str__(self) -> str:
		return str(self.__dict__)

	def __repr__(self) -> str:
		return str(self.__dict__)