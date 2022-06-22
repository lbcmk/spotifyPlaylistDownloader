from selenium import webdriver
import selenium
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
import selenium.webdriver.support.expected_conditions as EC
import os
from time import sleep
from os import listdir
from os.path import isfile, join
from selenium.webdriver.support.ui import WebDriverWait 
from dotenv import load_dotenv
import requests 
from slugify import slugify
load_dotenv()

import json
from yt_dlp import YoutubeDL
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from os.path import exists
from io import BytesIO

"""
Variables Section
"""
SPOTIFY_PLAYLIST_ID = "Playlist ID"
SPOTIFY_API_KEY = "token" # https://developer.spotify.com/documentation/web-playback-sdk/quick-start/
SPOTIFY_MARKET_LOCATION = "CA" # https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Decoding_table

class bot:
    def __init__(self, key, playlist_id, market, skip_to=0):
        os.makedirs(os.path.join(os.getcwd(), f"spotify/{SPOTIFY_PLAYLIST_ID}"), exist_ok=True)
        self.directory = os.path.join(os.getcwd(), "spotify")
        self.download_list = []
        self.trackdatafull = []
        self.trackdata = []
        self.get_tracks(key, playlist_id, market)
        self.options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_settings.popups": 0,
             "download.default_directory": self.directory, #IMPORTANT - ENDING SLASH V IMPORTANT
             "directory_upgrade": True, 
             "profile.default_content_setting_values.notifications" : 2}
        self.options.add_argument("--disable-notifications")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.options.add_experimental_option("prefs", prefs)
        self.n = skip_to
        
        
    def start(self, id):
        if(len(self.download_list) > 0):   
            self.driver = webdriver.Chrome(options=self.options)
            self.wait = WebDriverWait(self.driver, 60)
            data = self.trackdata
            for self.number, self.i in enumerate(self.download_list[self.n:]):
                try:
                    if(self.i[0] == "#"):
                        self.i = self.i.replace("#", "", 1) # removes the hash from the start of a string to make sure it doesn't search youtube as a hashtag

                    self.driver.get(f"https://www.youtube.com/results?search_query={self.i}")
                    element = self.find(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/div/div[1]/div/h3/a")
                    link = f'{element.get_attribute("href")}'
                    self.driver.get(link);
                    
                    data[self.number]["track"]["video_url"] = link
                    self.trackdatafull.append(data[self.number])
                    
                except TimeoutError:
                    print(f"Can't download song #{self.number+1} - {self.i}")
            sleep(2)
            self.trackdata = data
            f = open(f"spotify/{id}/playlist.json", "w")
            f.truncate(0)
            json.dump(self.trackdatafull, f, sort_keys=True, indent='\t', separators=(',', ': '))
            f.close()
            self.driver.close()
        else:
            print("No new songs to download")
        
        self.download(id)
        
    
    def download(self, id):
        f = open(f"spotify/{id}/playlist.json", "r")
        playlist_json = json.load(f)
        f.close()

        for i in playlist_json: # loops for every song in the playlist.json file
            title, first_artist = i["track"]["name"], i["track"]["artists"][0]["name"]
            while(title[-1] in '"!@#$%^&*()-+?_=,<>/"'): # removes speacial characters from the name to make sure it doesn't create unwanted behaviour in file managers
                    title = title[:-1]
            if(len(first_artist) > 0):            
                while(first_artist[0] in '"!@#$%^&*()-+?_=,<>/'):
                    first_artist = first_artist[1:]
            for k in '#"/\*|:?><':
                title = title.replace(k, '')
                first_artist = first_artist.replace(k, '')

            filePath = f"spotify/{id}/songs/{first_artist} - {title}.mp3"

            if(exists(filePath)):
                continue; # skips if the file already exists
            if(not "video_url" in i["track"]):
                continue; # if there is no video url in the json element then it skips it

            video_info = YoutubeDL().extract_info(
                url=str(i["track"]["video_url"]), download=False
            )

            options = {
                'format':'bestaudio/best',
                'extractaudio':True,
                'audioformat':'mp3',
                'outtmpl':filePath,
                'noplaylist':True,
                'nocheckcertificate':True,
                'proxy':"",
                'addmetadata':True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }

            with YoutubeDL(options) as ydl:
                ydl.download([video_info['webpage_url']])


            song = EasyID3(filePath)
            song['title'] = str(i["track"]["name"])
            song['album'] = str(i["track"]["album"]["name"])
            artists = []
            for j in i["track"]["artists"]:
                artists.append(j.get("name"))
            song['artist'] = artists
            song["tracknumber"] = str(i["track"]["track_number"])
            
            song.save()

            song = ID3(filePath)

            response = requests.get(i["track"]["album"]["images"][0]["url"])
            img = BytesIO(response.content)

            song['APIC'] = APIC(
                      encoding=3,
                      mime='image/jpeg',
                      type=3, desc=u'Cover',
                      data=img.getvalue()
                    )
                        
            song.save()
            

    def waiting(self, by, element, method):
        try:
            self.wait.until(method((by, element)))
        except:
            raise TimeoutError
        
    def changename(self):
        sleep(1)
        onlyfiles = [f for f in listdir(self.directory) if isfile(join(self.directory, f))]
        while onlyfiles[0].split(".")[-1] == "crdownload":
            sleep(0.5)
            onlyfiles = [f for f in listdir(self.directory) if isfile(join(self.directory, f))]
        old_file = os.path.join(self.directory, onlyfiles[0])
        digits_to_add = len(str(self.total)) - len(str(self.number+self.n+1))
        new_file = os.path.join(os.path.join(self.directory, "playlist"), f"{'0'*digits_to_add}{self.number+self.n+1}. {slugify(self.song_name)}.mp3")
        os.replace(old_file, new_file)
        
        
    def find(self, by, element, method=EC.presence_of_element_located):  
        self.waiting(by, element, method)
        return self.driver.find_element(by, element)
    
    
    def get_tracks(self, key, id, market):
        self.total = requests.get(f"https://api.spotify.com/v1/playlists/{id}/tracks?market={market}&fields=total", headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"}).json()['total']        
        
        if not exists(f"spotify/{id}/playlist.json"):
            with open(f"spotify/{id}/playlist.json", 'w'): pass

        f = open(f"spotify/{id}/playlist.json", "r")
        if(os.stat(f.name).st_size == 0):
            f.close()
            f = open(f"spotify/{id}/playlist.json", "w")
            f.write("[]")
            f.close()
            f = open(f"spotify/{id}/playlist.json", "r")
        data = json.load(f)
        f.close()

        self.trackdatafull = data;

        for n in range(divmod(self.total, 100)[0] + 1):
            res = requests.get(f"https://api.spotify.com/v1/playlists/{id}/tracks?market={market}&fields=items(track.name%2Ctrack.artists.name),items.track.album.images,items.track.track_number,items.track.album.name,items.track.id,items.track.duration_ms&offset={n*100}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"}).json()
            for i in res["items"]:
                if("is_local" in i["track"]):
                    if(i["track"]["is_local"] == True):
                        continue; #skips local files
                skip = False;      
                for dict in data:
                    if (dict["track"]["id"] == i["track"]["id"] and "video_url" in dict["track"]):
                        skip = True;
                title, first_artist = i["track"]["name"], i["track"]["artists"][0]["name"]
                while(title[-1] in '"!@#$%^&*()-+?_=,<>/"'): # removes speacial characters from the name to make sure it doesn't create unwanted behaviour in file managers
                    title = title[:-1]
                if(len(first_artist) > 0):            
                    while(first_artist[0] in '"!@#$%^&*()-+?_=,<>/'):
                        first_artist = first_artist[1:]
                    
                if(skip == False):
                    self.download_list.append(f'{title} by {first_artist} (official audio)')
                    self.trackdata.append(i)
        

if __name__ == "__main__":
    v1 = bot(SPOTIFY_API_KEY, SPOTIFY_PLAYLIST_ID, SPOTIFY_MARKET_LOCATION, skip_to=0) 
    v1.start(SPOTIFY_PLAYLIST_ID)
