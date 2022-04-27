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
import os 
from dotenv import load_dotenv
import requests 
from slugify import slugify
load_dotenv()


"""
Variables Section 

"""
SPOTIFY_PLAYLIST_ID = "0Hx4aQ2xTb4TKl5Z56DJh0"
SPOTIFY_API_KEY = "BQAI2L9IZ8l56h020jeFQnoSff2HNTcZhQ-a1uYCAcyrJfSFIpb6j5icKS__PEtPw_aJT2XmOB4lvOJ60oImk5f0s0TBqDgwzDwA8dlZuLap2440474tPw2l2ObNdeOsxyHD2MEvmBRD0CPk29yMIJp6nZSsT47ck8ZPaKuLF8joshfspUmKWxVDl3AZiLKwMlyl6dgoZW0oeluD3tY_6leKLrAznpQpgA-V2fU"

class bot:
    def __init__(self, key, playlist_id, skip_to=0):
        os.makedirs(os.path.join(os.getcwd(), "spotify/playlist"), exist_ok=True)
        self.directory = os.path.join(os.getcwd(), "spotify")
        self.download_list = [] 
        self.get_tracks(key, playlist_id)
        self.options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_settings.popups": 0,
             "download.default_directory": self.directory, #IMPORTANT - ENDING SLASH V IMPORTANT
             "directory_upgrade": True, 
             "profile.default_content_setting_values.notifications" : 2}
        self.options.add_argument("--disable-notifications")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.options.add_experimental_option("prefs", prefs)
        self.n = skip_to
        
        
    def start(self):
        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 60)
        for self.number, self.i in enumerate(self.download_list[self.n:]):
            try:
                self.driver.get(f"https://www.youtube.com/results?search_query={self.i}")
                element = self.find(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/div/div[1]/div/h3/a")
                link = f'{element.get_attribute("href")[:19]}pi{element.get_attribute("href")[19:]}'
                self.driver.get(link)
                self.song_name = self.find(By.XPATH, "/html/body/section[1]/div/div[2]/div[2]/div/div[1]/div/div[2]/b").text.split("\n")[0]
                self.download(link)
                self.changename()
            except TimeoutError:
                print(f"Can't download song #{self.number+1} - {self.i}")
        sleep(15)
        self.driver.close()
        
    
    def waiting(self, by, element, method):
        try:
            self.wait.until(method((by, element)))
        except:
            raise TimeoutError

    
    
    def download(self, link):
        self.driver.get(link) # get download link 
        self.find(By.XPATH, "/html/body/section[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/button[2]", EC.element_to_be_clickable).click() # click Audio btn 
        self.find(By.XPATH, "/html/body/section[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/table/tbody/tr[2]/td[3]/button", EC.element_to_be_clickable).click() # click convert btn 
        self.find(By.XPATH, "/html/body/section[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/table/tbody/tr[2]/td[3]/button/a", EC.element_to_be_clickable).click() # download
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[1])
        self.driver.close()
        self.driver.switch_to.window(windows[0])
        
        
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
    
    
    def get_tracks(self, key, id):
        self.total = requests.get(f"https://api.spotify.com/v1/playlists/{id}/tracks?market=CA&fields=total", headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"}).json()['total']        
        for n in range(divmod(self.total, 100)[0] + 1):
            res = requests.get(f"https://api.spotify.com/v1/playlists/{id}/tracks?market=CA&fields=items(track.name%2Ctrack.artists.name)&offset={n*100}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"}).json()    
            for i in res["items"]:
                self.download_list.append(f'{i["track"]["name"]} by {i["track"]["artists"][0]["name"]} lyrics')
        
if __name__ == "__main__":
    v1 = bot(SPOTIFY_API_KEY, SPOTIFY_PLAYLIST_ID, skip_to=0) 
    v1.start()
