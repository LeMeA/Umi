from random import randint
from youtubesearchpython import VideosSearch
import pytube


class Playlist:
	def __init__(self):
		self.tracks = []
		self.idx = 0
		self.type = None
		self.shuffled = []

	def get_user_from_url(self, url):
		user = 4
		return url.split('/')[user]

	def get_playlist_from_url(self, url):
		playlist = 6
		return int(url.split('/')[playlist])

	def get_playlist(self, url, clients):
		if 'yandex' in url:
			user = self.get_user_from_url(url)
			playlist_num = self.get_playlist_from_url(url)
			pl = clients['YANDEX'].users_playlists(playlist_num, user)

			if pl is None:
				return False

			self.tracks = pl['tracks']
			self.type = 'YANDEX'
		elif 'spotify' in url:
			self.tracks = clients['SPOTIFY'].playlist_tracks(url)["items"]
			if self.tracks is None:
				return False
			self.type = 'SPOTIFY'
		else:
			return False

		self.idx = 0
		return True

	def download_track(self, track_path):
		if self.idx == len(self.tracks):
			self.idx = 0
		track_name = ""
		if self.type == 'YANDEX':
			track = self.tracks[self.idx].fetch_track()
			track_name = track['title'] + " " + track['artists'][0]['name']
		elif self.type == 'SPOTIFY':
			track_name = self.tracks[self.idx]["track"]["name"] + ' ' + self.tracks[self.idx]["track"]["artists"][0]["name"]

		res = VideosSearch(track_name, limit=2).result()
		link = res['result'][0]['link']
		yt = pytube.YouTube(link)
		streams = yt.streams.filter(only_audio=True)
		i = 0
		while i + 1 < len(streams) and streams[i + 1].mime_type == "audio/mp4":
			i += 1
		streams[i].download(output_path=track_path, filename='track.mp3')
		track = self.tracks[self.idx]
		self.idx += 1
		return res['result'][0]

	def set_shuffle_track(self):
		self.idx = randint(0, len(self.tracks) - 1)
		while self.idx in self.shuffled:
			self.idx = randint(0, len(self.tracks) - 1)
		self.shuffled.append(self.idx)
		if len(self.shuffled) > len(self.tracks) / 2:
			self.shuffled.clear()

	def empty(self):
		if self.idx == len(self.tracks):
			return True
		else:
			return False
