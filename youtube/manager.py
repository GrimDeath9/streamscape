from datetime import datetime, timedelta, date
from time import sleep
import os

from . import bulk
from .stream_manager import StreamManager
from .stream_format import StreamInfo
from .config import Config

class Channel:
	def __init__(self, id):
		self.id = id
		self.live_url = f'https://www.youtube.com/channel/{id}/live'

def __time_next(mod_factor: int, refresh: int):
	now = datetime.now()
	refreshed = now + timedelta(minutes=refresh)
	mod_refreshed = int(refreshed.strftime("%M")) % mod_factor
	delta = timedelta(minutes=refresh - mod_refreshed)
	next_time = (now+delta).replace(microsecond=0, second=0)
	return now, next_time

def __time_til(time: str, time_format: str):
	next_time = datetime.strptime(f'{date.today()} {time}', f'%Y-%m-%d {time_format}')
	return (next_time - datetime.now()).total_seconds()

def __get_new_lives(channels: list[Channel], downloaded):
	live_urls = [i.live_url for i in channels]
	new = [i for i in bulk.get_live_ids(live_urls) if i not in downloaded]
	pages = bulk.request([f'https://youtu.be/{i}' for i in new])
	return [StreamInfo(stream_id, stream_link) for stream_id, stream_link in zip(new, pages)]

def __read_channels(filepath: str):
	channels = []
	for file in os.listdir(f'./{filepath}'):
		with open(f'./{filepath}/{file}') as f:
			channels.extend([i.split('\n')[0] for i in f.readlines()])
	return channels

def make_folders(config: Config):
	output = config.output.path
	if not os.path.exists(output): os.mkdir(output)
	log = config.logging
	if not os.path.exists(log): os.mkdir(log)

def start(filepath = './config.toml'):
	config = Config(filepath)
	make_folders(config)
	channels = [Channel(i) for i in __read_channels(config.channels)]
	downloaded = []
	while True:
		print(f'[INFO] Checking for streams from {len(channels)} channels')
		new_streams = __get_new_lives(channels, downloaded)
		for stream in new_streams:
			print(f"[INFO] Downloading {stream.id}")
			StreamManager(config, stream).start()
			downloaded.append(stream.id)
		now, next_time = __time_next(config.cycle.mod, config.cycle.interval)
		print(f"[INFO] Finished run:\t{now.strftime(config.cycle.format)}")
		print(f"\tNext run:\t{next_time.config.cycle.format}")
		sleep(__time_til(next_time, config.cycle.format))