# spotifyPlaylistDownloader
Original code written by LotusDeath69 (found at https://github.com/LotusDeath69/spotifyPlaylistDownloader)

## Disclaimers:
- This code was written and ran in Windows 10; other OS compatibility is unknown. <br>
- This code was also tested with Latin characters in mind. Although it should work with other writing systems, compatibility is not guaranteed. <br>

## Description:
Downloads a Spotify playlist

## Prerequisite for v2:  
```bash
pip install -r requirements.txt  
```
chromedriver (https://chromedriver.chromium.org/downloads) <br>
ffmpeg (https://ffmpeg.org/download.html) <br>
Spotify token (https://developer.spotify.com/documentation/web-playback-sdk/quick-start/) <br>
Spotify playlist id: (i.e. 0Hx4aQ2xTb4TKl5Z56DJh0) <br>

## How to Use: <br>
Download <code>chromedriver</code> and <code>ffmpeg</code> and place the executables files in the same folder as scrapper.py. <br>
Input Spotify API token, playlist id, and country market in the Variables Section. <br>
```python
SPOTIFY_PLAYLIST_ID = "0Hx4aQ2xTb4TKl5Z56DJh0"
SPOTIFY_API_KEY = "token"
SPOTIFY_MARKET_LOCATION = "CA"
```
run by typing <code>python scrapper.py</code> in the terminal

## Built Using:
* Selenium (Automated Chrome)
* YT-DLP (Youtube Video Downloader)
* Mutagen (ID3/Metadata Editor)
* requests (Spotify API calls)
* JSON (Storing API data with JSON)

## Additions:
- [x] Playlist Persistance
    - [x] JSON file to store playlist data
- [x] YT-DLP download
- [x] Add ID3 data to mp3 using mutagen
- [x] Stop YT-DLP from downloading files that are already downloaded
- [ ] Equaliser for equal volume songs

## Contributing
I will not be monitoring this repository, the easiest way to contribute would be to fork this repo.

## License
Distributed under the [MIT License](https://choosealicense.com/licenses/mit/). See <code>LICENSE.txt</code> for more information.