import sys, os
import tempfile

import yt_dlp
import mpv

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
        self.urllist = []
        self.playlist = []
        self.duration = ''

    def yt_search(self, text):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            video = ydl.extract_info(f"ytsearch:{text}", download=False)['entries'][0]
            link = video['webpage_url']
            title = video['title']
            duration = video['duration']
        return link,title,duration

    def add(self, text):
        url,title,duration = self.yt_search(text)
        
        self.urllist.append(url)
        self.playlist.append(title)
        print("Added:",title)

    def play(self):
        self.yt_down(self.urllist[self.pos])

        self.player.play(self.song_path)        # This uses MPV player
        print("Now Playing --> ", self.curr_title())

    def yt_down(self,link):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
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
    def rm(self, num):
        del self.playlist[num]
        del self.urllist[num]
    def curr_link(self):
        return self.urllist[self.pos]
    def curr_title(self):
        return self.playlist[self.pos]
    def get_duration(self):
        return self.get_duration

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

    elif command in ['next','nx']:
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
            print(i+1, ':',song)
        if not p.playlist:
            print("List is empty, add some songs first")

    elif command in ['goto', 'gt']:
        if not utext or not utext.isdecimal():
            print("ERROR: Enter a number from playlist")
        else:
            num = int(utext) - 1
            if num < len(p.playlist) and num >= 0:
                p.goto(int(utext)-1)
            else:
                print("ERROR: Can't go to that position, Position doesn't exists")

    elif command in ['del', 'rm']:
        if not utext or not utext.isdecimal():
            print("ERROR: Enter a number from playlist")
        else:
            num = int(utext) - 1
            if num >= 0 and num < len(p.playlist):
                p.rm(int(utext))
                print("Deleted")
            else:
                print("ERROR: Can't delete, position doesn't exists")

    elif command in ['e','q','exit' , 'quit', 'end']:
        sys.exit()

    elif command in ['h','help']:
        print("\nAvailable commands:")
        print("""
        add song : add, a
        play song : play, p
        next song : next, nx
        prev song : prev, pv
        show playlist : list, ls
        goto position : goto, gt
        delete song : del, rm
        exit : exit, quit, e, q
        help : help, h
        """)
    
    else:
        print("Incorrect Command. Type exit to exit.")
        

if __name__ == '__main__':
    p = Alex()
    print("****************************************")
    print("Hi this is Alex, a youtube music player.")

    print("Start by adding songs with command add, playing songs with play or ask for help.")
    while True:
        inp = input("\nWhat is thy command?\n")
        interface(inp)