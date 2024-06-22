from threading import Thread
from subprocess import Popen, DEVNULL
from discord_webhook import DiscordWebhook, DiscordEmbed
import time
import os

from .stream_format import StreamInfo
from .config import Config

class _StreamEmbed:
	def __init__(self, stream: StreamInfo, webhook_url: str):
		self.webhook = DiscordWebhook(url=webhook_url)
		self.embed = DiscordEmbed()
		self.stream = stream
		self.response = ""
		
	def send(self):
		self.embed.set_title(self.stream.title)
		self.embed.set_url(self.stream.url)
		self.embed.set_color("E3E91D")
		self.embed.set_author(name = self.stream.author, url = self.stream.author_url)
		self.embed.set_thumbnail(self.stream.author_icon)
		self.embed.set_image(self.stream.thumbnail)
		self.embed.set_timestamp()
		self.embed.add_embed_field(name="Start:", value=self.__time_now(), inline=False)
		self.webhook.add_embed(self.embed)
		self.response = self.webhook.execute()

	def finished(self):
		self.webhook.remove_embed(0)
		self.embed.set_color("00F042")
		self.embed.set_timestamp()
		self.embed.add_embed_field(name="Finish:", value=self.__time_now(), inline=False)
		self.webhook.add_embed(self.embed)
		self.response = self.webhook.edit()

	@staticmethod
	def __time_now():
		zero_remover = '#' if os.name == 'nt' else '-'
		return time.strftime('%a %b. %{}d %Y %{}I:%M %p'.format(zero_remover, zero_remover))


class StreamManager(Thread):
	def __init__(self, config: Config, stream: StreamInfo):
		Thread.__init__(self)
		self.stream = stream
		self.embed = _StreamEmbed(stream, config.webhook)
		self.config = config
		args = [config.ytarchive]
		args.extend(self.config.output.args)
		args.extend([stream.url, config.output.quality])
		self.args = args
	
	def run(self):
		log_file = open(f'{self.config.logging}/{self.stream.id}.txt', 'w') if self.config.logging else DEVNULL
		downloader = Popen(self.args, stdout=log_file, stderr=log_file)
		self.embed.send()
		downloader.wait()
		self.embed.finished()