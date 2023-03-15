from .playlist import Playlist
from .queue_ import Queue
from ...config import PATH_TO_SERVERS


class Player:
    def __init__(self, guild_id):
        self.playlists = {'QUEUE': Queue(), 'PLAYLIST': Playlist()}
        self.mode = 'QUEUE'
        self.track_path = PATH_TO_SERVERS + str(guild_id)  # + '/track.mp3'
        self.cur_track = None
        self.f_shuffle = False
        self.paused = False

    def download_next(self):
        """Downloads new track from queue or playlist"""
        print('download_next')
        if self.mode == 'PLAYLIST' and self.f_shuffle:
            self.playlists[self.mode].set_shuffle_track()
        self.cur_track = self.playlists[self.mode].download_track(self.track_path)
        print('download_next end')

    def stop(self):
        """Reset current playlist"""
        self.playlists['QUEUE'] = Queue()
        self.playlists['PLAYLIST'] = Playlist()
        self.mode = 'QUEUE'

    def turn_shuffle(self):
        """Turn on/off shuffle tracks for playlist"""
        if self.mode == 'PLAYLIST':
            self.f_shuffle = not self.f_shuffle
            return True
        return False

    def add_to_queue(self, query):
        """Search and add new track to queue"""
        res = self.playlists['QUEUE'].add_track(query)
        self.mode = 'QUEUE'
        return res

    def set_playlist(self, url, clients):
        """Search and set playlist"""
        if self.playlists['PLAYLIST'].get_playlist(url, clients) is False:
            return False
        self.mode = 'PLAYLIST'
        return True

    def empty(self):
        """Check if queue/playlist is empty"""
        if self.mode == 'QUEUE' and self.playlists[self.mode].empty():
            self.cur_track = None
            return True
        if self.mode == 'PLAYLIST' and self.f_shuffle is False and self.playlists[self.mode].empty():
            self.cur_track = None
            return True
        return False

    def track_title(self):
        """Returns title of track"""
        return self.cur_track['title']

    def track_cover(self):
        """Return cover of track"""
        return self.cur_track['thumbnails'][0]['url']

