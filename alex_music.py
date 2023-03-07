import mpv
import sys, os
from youtubesearchpython import VideosSearch
import yt_dlp
import tempfile

class Alex():
    player = mpv.MPV()
    song_path = tempfile.NamedTemporaryFile(suffix='.m4a').name
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a'
        }],
        'outtmpl': song_path
    }


    def __init__(self):
        self.pos = 0
        self.urllist = []
        self.playlist = []
        self.curr_link = None
        self.curr_title = None

    def search(self, text):
        videos = VideosSearch(text, limit=1)
        link = videos.result()["result"][0]["link"]
        title = videos.result()["result"][0]["title"]
        return link,title

    def add(self, text):
        url,title = self.search(text)
        print("Added:",title)
        self.urllist.append(url)
        self.playlist.append(title)

    def play(self):
        self.download(self.urllist[self.pos])

        self.curr_title = self.playlist[self.pos]
        self.curr_link = self.urllist[self.pos]
        
        print("Now Playing --> ", self.curr_title)
        self.player.play(self.song_path)

    def download(self,link):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            print("Downloading link", link)
            try:
                os.remove(self.song_path)
            except Exception as e:
                print(e)
            error_code = ydl.download(link)
    
    def next(self):
        self.pos += 1
        self.play()
    def prev(self):
        self.pos -= 1
        self.play()
    def goto(self, num):
        self.pos = num
        self.play()


def parse(text):
    splitted = text.split()
    command = splitted[0]
    utext = ' '.join(splitted[1:])

    if command == 'add':
        p.add(utext)
    elif command == 'next':
        p.next()
    elif command == 'prev':
        p.prev()
    elif command == 'goto':
        p.goto(int(utext)-1)
    elif command == 'play':
        if utext:
            p.add(utext)
            p.pos = len(p.playlist) - 1
            p.play()
        else:
            p.play()
    elif command == 'playlist':
        for i,song in enumerate(p.playlist):
            print(i+1, ':',song)
    elif command == 'current':
            print(p.curr_title)
    elif command in ['exit' , 'quit']:
        sys.exit()
    elif command == 'help':
        print("\nAvailable commands:")
        print('add, play, next, prev, playlist, goto, current, help, exit, quit')
        

if __name__ == '__main__':
    p = Alex()
    print("Hi this is Alex, a youtube music player")
    print("Start by adding songs with command add and playing songs with play")
    while True:
        inp = input("\nWhat is thy command?\n")
        parse(inp)

