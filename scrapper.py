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
SPOTIFY_API_KEY = "BQBSHST6MibuHA4-TnTHUl5ih-lLTjBuhSzYi636ij87KFa1QJnUYM6RXCIEiZUWtZUBK8GUYTDAxMYvtPf6ZmU7LB-mR0DPFBNmnrfUGrY72Cgo5-6xA3MtKHnGUzOest5UfrUTZ3FqgWMTAaqvIZzltFsmdOfbuJmtI8i_5CrleSLfWtmi6Vw5MkK-3zhcEORXYcXC30DNSl8dmJvLpkndSJO7MEh93l3IRdE"



class bot:
    def __init__(self, key, playlist_id, n=0):
        os.makedirs(os.path.join(os.getcwd(), "spotify/playlist"), exist_ok=True)
        self.directory = os.path.join(os.getcwd(), "spotify")
        self.download_list = [] 
        self.get_tracks(key, playlist_id)
        options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_settings.popups": 0,
             "download.default_directory": self.directory, #IMPORTANT - ENDING SLASH V IMPORTANT
             "directory_upgrade": True, 
             "profile.default_content_setting_values.notifications" : 2}
        options.add_argument("--disable-notifications")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 60)
        self.n = n
        self.start()
        
        
    def start(self):
        for self.number, i in enumerate(self.download_list[self.n:]):
            self.driver.get(f"https://www.youtube.com/results?search_query={i}")
            element = self.find(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/div/div[1]/div/h3/a")
            link = f'{element.get_attribute("href")[:19]}pi{element.get_attribute("href")[19:]}'
            self.driver.get(link)
            self.song_name = self.find(By.XPATH, "/html/body/section[1]/div/div[2]/div[2]/div/div[1]/div/div[2]/b").text.split("\n")[0]
            self.download(link) 
            self.changename()
        sleep(15)
        self.driver.close()
        
    
    def waiting(self, by, element, method):
        try:
            self.wait.until(method((by, element)))
        finally:
            pass 
    
    
    def download(self, link):
        self.driver.get(link) # get download link 
        self.find(By.XPATH, "/html/body/section[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/button[2]", EC.element_to_be_clickable).click() # click Audio btn 
        self.find(By.XPATH, "/html/body/section[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/table/tbody/tr[2]/td[3]/button", EC.element_to_be_clickable).click() # click convert btn 
        self.find(By.XPATH, "/html/body/section[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/table/tbody/tr[2]/td[3]/button/a", EC.element_to_be_clickable).click() # download
        windows = self.driver.window_handles
        self.driver.close()
        self.driver.switch_to.window(windows[1])
        
        
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
        
v1 = bot(SPOTIFY_API_KEY, SPOTIFY_PLAYLIST_ID) 