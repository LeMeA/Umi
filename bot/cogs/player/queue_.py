from youtubesearchpython import VideosSearch
import pytube


class Queue:
    def __init__(self):
        self.queue = []

    def search(self, query):
        res = VideosSearch(query, limit=2).result()
        duration_min = res['result'][0]['duration'].split(":")
        if int(duration_min[0]) > 7:  # 7 minutes more than needs track
            return None
        link = res['result'][0]['link']
        return res['result'][0]

    def add_track(self, query):
        track_info = self.search(query)
        if track_info is not None:
            self.queue.append(track_info)
            return True
        else:
            return False

    def download_track(self, track_path):
        print('download start')
        if len(self.queue) == 0:
            return None

        track_info = self.queue.pop(0)
        yt = pytube.YouTube(track_info['link'])
        streams = yt.streams.filter(progressive=True, file_extension='mp4')
        streams.order_by('resolution').desc().first().download(track_path, 'track.mp3')
        #i = 0
        #while i + 1 < len(streams) and streams[i + 1].mime_type == "audio/mp4":
        #    i += 1
        #print(f'found {streams[i]}')
        #streams[i].download(output_path=track_path, filename='track.mp3')
        print('downloaded')
        return track_info

    def empty(self):
        if len(self.queue) == 0:
            return True
        return False
