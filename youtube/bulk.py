import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
from typing import Callable

async def __multi(session, function: Callable, urls: list[str]):
	tasks = []
	for url in urls:
		task = asyncio.create_task(function(session, url))
		tasks.append(task)
	results = await asyncio.gather(*tasks)
	return results

async def __sessioner(function: Callable, urls: list[str]):
	connector = aiohttp.TCPConnector(limit=10)
	async with aiohttp.ClientSession(connector=connector) as session:
		output = await __multi(session, function, urls)
		return output

def __main(function: Callable, urls: list[str]):
	loop = asyncio.get_event_loop()
	return loop.run_until_complete(__sessioner(function, urls))

async def __request(session, url):
	async with session.get(url) as r:
		return await r.text()

def __get_var_init_resp(soup: BeautifulSoup):
	index = -1
	for i, _item in enumerate(soup.find_all('script')):
		if _item.text.startswith('var ytInitialPlayerResponse'):
			index = i
	return soup.find_all('script')[index].text[30:-1] if index != -1 else ''

async def __check_live(session, url):
	async with session.get(url) as r:
		request = await r.text()
		try:
			var = json.loads(__get_var_init_resp(BeautifulSoup(request, 'lxml')))
			is_live = var['playabilityStatus']['status'] == 'OK'
			return var['videoDetails']['videoId'] if is_live else ''
		except (json.JSONDecodeError, KeyError):
			return ''

def get_live_ids(urls: list[str]):
	out = __main(__check_live, urls)
	return [i for i in out if i]

def request(urls: list[str]):
	return __main(__request, urls)