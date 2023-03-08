import sys, os
import threading
import time, tempfile
import logging

import yt_dlp
import mpv

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')

def blockPrint():
    sys.stdout = open(os.devnull,'w')
def enablePrint():
    sys.stdout = sys.__stdout__


class Alex():
    player = mpv.MPV()
    song_path = tempfile.NamedTemporaryFile(suffix='.m4a').name

    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        # See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a'
        }],
        'outtmpl': song_path
    }


    def __init__(self):
        self.pos = 0
        self.playlist = [] # Contains dictionaries of songs with keys: url, title and duration
        self.playing = 0
        self.thread = None
    def yt_search(self, text):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            video = ydl.extract_info(f"ytsearch:{text}", download=False)['entries'][0]
            link = video['webpage_url']
            title = video['title']
            duration = video['duration']
        return link,title,duration

    def add(self, text):
        song = {}
        song['url'], song['title'], song['duration'] = self.yt_search(text)
        self.playlist.append(song)
        print("Added:",song['title'])

    def play(self):

        if self.playing:
            logging.debug(f"pos:{self.pos}, playing:{self.playing}, Another instance is playing")
            self.playing = 0
            time.sleep(1)
            logging.debug(f"pos:{self.pos}, playing:{self.playing}, Another instance is still playing")
            
        self.thread = threading.Thread(target = self.bgplay, args=())
        logging.debug(f"pos:{self.pos}, Defined a thread and sent a start command")
        self.thread.start()
        
    def bgplay(self):
        self.yt_down(self.playlist[self.pos]['url'])
        self.playing = 1
        logging.debug(f"pos:{self.pos}, playing:{self.playing} Started the player thread")
        self.player.play(self.song_path)        # This uses MPV player
        print(f"Now Playing --> {self.get_title()} ({self.get_duration('m')}m)")

        a = time.time()
        while self.playing and time.time()- a < self.get_duration():
            time.sleep(0.5)
        logging.debug(f"pos:{self.pos}, playing:{self.playing}, Playback ended")
        if self.playing and self.pos+1<len(self.playlist):
            logging.debug(f"pos:{self.pos}, playing:{self.playing}, Doing next since single is true")
            self.pos +=1 
            self.bgplay()
        self.playing = 0
        logging.debug(f"pos:{self.pos}, playing:{self.playing}, Thread Ended")

    def yt_down(self,link):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                os.remove(self.song_path)
            except Exception as e:
                print(e)
            error_code = ydl.download(link)
    
    def next(self):
        logging.debug(f"pos:{self.pos}, Doing next")
        if self.pos+1 < len(self.playlist):
            self.pos += 1
            self.play()
    def prev(self):
        logging.debug(f"pos:{self.pos}, Doing prev")
        if self.pos >0 and self.pos <len(self.playlist):
            self.pos -= 1
            self.play()
    def goto(self, num):
        logging.debug(f"pos:{self.pos}, Doing goto")
        if num < len(self.playlist) and num >= 0:
            self.pos = num
            self.play()
    def rm(self, num):
        logging.debug(f"pos:{self.pos}, Doing del")
        if num < len(self.playlist) and num >= 0:
            del self.playlist[num]

    def get_url(self):
        return self.playlist[self.pos]['url']
    def get_title(self):
        return self.playlist[self.pos]['title']
    def get_duration(self,frame='s'):
        if frame == 'm':
            return round(self.playlist[self.pos]['duration']/60,1)
        return self.playlist[self.pos]['duration']

def interface(text):
    """serves as a interface for user to an Alex() instance

    Args:
        text (str): User input where first word is a command for the player
    """
    splitted = text.split()
    if splitted:
        command = splitted[0]
        utext = ' '.join(splitted[1:])
    else:
        interface(input())
        return
    if command in ['add','a']:
        if utext:
            p.add(utext)
        else:
            print("ERROR: Type song name after add command")

    elif command in  ['play','p']:
        if utext:
            p.add(utext)
            p.pos = len(p.playlist) - 1
            p.play()
        elif p.playlist:
            p.play()
        else:
            print("ERROR: Add songs to play by adding song name afterwards")

    elif command in ['next','nx', 'n']:
        if p.pos+1 < len(p.playlist):
            p.next()
        else:
            print("ERROR: Can't next, reached max next")

    elif command in ['prev','pv']:
        if p.pos >0 and p.pos <len(p.playlist):
            p.prev()
        else:
            print("ERROR: Can't goto previous, reached max prev")

    elif command in  ['list', 'playlist', 'ls']:
        for i,song in enumerate(p.playlist):
            if p.pos == i:
                print(f"--> {i+1} : {song['title']} ({round(song['duration']/60,1)}m)")
            else:
                print(f"    {i+1} : {song['title']} ({round(song['duration']/60,1)}m)")
        if not p.playlist:
            print("List is empty, add some songs first")

    elif command in ['goto', 'gt']:
        if not utext or not utext.isdecimal():
            print("ERROR: Enter a number from playlist")
        else:
            num = int(utext) - 1
            if num < len(p.playlist) and num >= 0:
                p.goto(num)
            else:
                print("ERROR: Can't go to that position, Position doesn't exists")

    elif command in ['del', 'rm']:
        if not utext or not utext.isdecimal():
            print("ERROR: Enter a number from playlist")
        else:
            num = int(utext)
            if num > 0 and num <= len(p.playlist):
                p.rm(num-1)
                print("Deleted")
                if p.pos and p.pos >= num-1:
                    p.pos -= 1

            else:
                print("ERROR: Can't delete, position doesn't exists")

    elif command in ['e','q','exit' , 'quit', 'end']:
        print("exited")
        os._exit(1)
        sys.exit()
        

    elif command in ['h','help']:
        print("Available commands:")
        print("""
        add song:       add, a
        play song:      play, p
        next song:      next, nx, n
        prev song:      prev, pv
        show playlist:  list, ls
        goto position:  goto, gt
        delete:         del, rm
        exit:           exit, quit, q
        help:           help, h""")
    
    else:
        print("Incorrect Command. Type q to exit.")
        

if __name__ == '__main__':
    p = Alex()
    print("****************************************")
    print("Hi this is Alex, a youtube music player.")

    print("Start by adding and playing songs or ask for help.")
    while True:
        inp = input("\nWhat is thy command?\n")
        interface(inp)