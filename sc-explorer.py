import requests
import io
import math
import threading
import queue
import time

from pydub import AudioSegment
from pydub.playback import play

with open('client_id', 'r') as f:  # ! Place your client_id in a file named client_id (same directory)
    client_id = f.read().strip()

api_url = 'https://api-v2.soundcloud.com'
search_endpoint = '/search/tracks'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
}

song_window_queue = queue.Queue(maxsize=10)

def search_by_genre(genre, query="*"):
    request_url = api_url + search_endpoint + "?q=" + query + "&filter.genre=" + genre + "&sort=popular&client_id=" + client_id + "&locale=en"
    r = requests.get(request_url, headers=headers)
    assert r.status_code == 200
    return r.json()

def get_song_window(track_url, time_window_size_sec, time_window_position_sec):
    song = bytearray()
    url = track_url + '?client_id=' + client_id
    r = requests.get(url, headers=headers)
    assert r.status_code == 200
    out = r.json()
    r = requests.get(out['url'], headers=headers)
    assert r.status_code == 200
    m3u_file = r.text.split('\n')
    assert m3u_file[0] == '#EXTM3U'
    current_time = 0
    position = 5
    for i in range(5, len(m3u_file), 2):
        duration = math.ceil(float(m3u_file[i].split(":")[1][:-1]))
        if current_time + (duration/2) >= time_window_position_sec:
            position = i
            break
        current_time += duration
    
    current_time = 0
    for i in range(position, len(m3u_file), 2):
        duration = math.ceil(float(m3u_file[i].split(":")[1][:-1]))
        current_time += duration
        r = requests.get(m3u_file[i+1], headers=headers)
        assert r.status_code == 200
        song.extend(r.content)
        if current_time >= time_window_size_sec:
            break
    s = AudioSegment.from_mp3(io.BytesIO(bytes(song)))
    return s

def get_most_commented_song_window_position(client_id, track_id, comments_count, comments_per_request, track_duration_sec, time_window_size_sec, max_comments):
    comments_count = min(max_comments, comments_count)
    timeline = [0]*track_duration_sec
    for offset in range(0, comments_count, comments_per_request):
        comment_url = api_url+'/tracks/'+str(track_id)+'/comments?threaded=0&client_id=' + client_id + '&limit='+str(comments_per_request)+'&offset='+str(offset)
        r = requests.get(comment_url, headers=headers)
        assert r.status_code == 200
        response = r.json()['collection']
        for comment in response:
            if comment['timestamp'] is None:
                #print("[-] skipping comment: no timestamp?")
                continue
            else:
                timeline[comment['timestamp']//1000] += 1
    
    max_comments = sum(timeline[:time_window_size_sec])
    time_window_position = 0
    current_comments = max_comments
    for i in range(time_window_size_sec, track_duration_sec):
        current_comments += timeline[i]
        current_comments -= timeline[i-time_window_size_sec]
        if (current_comments > max_comments):
            max_comments = current_comments
            time_window_position = i-time_window_size_sec+1
        
    return time_window_position

def fill_song_queue_loop(genre):
    candidates = search_by_genre(genre)['collection']
    for song in candidates:
        if not song['commentable']:
            continue

        song_id = song['id']
        song_url = song['media']['transcodings'][0]['url']
        song_duration = song['duration']
        song_title = song['title']
        song_comment_count = song['comment_count']
        
        window_position = get_most_commented_song_window_position(client_id, song_id, song_comment_count, 200, song_duration, 10, 600)
        song_window = get_song_window(song_url, 10, window_position)
        song_window_queue.put({'title': song_title, 'window': song_window}, block=True, timeout=200)
#        print('[*] "' + song_title + '"   inserted into queue')

def main():
    while True:
        song = song_window_queue.get()
        print('[+] Playing: "' + song['title'] + '"')
        play(song['window'])
        input("Like?") # TODO: do the actual insertion to a playlist

if __name__ == "__main__":
    time.sleep(2)
    assert song_window_queue is not None
    threading.Thread(target=fill_song_queue_loop, args=('hiphoprap',)).start()
    print("Buffering song queue")
    time.sleep(10)
    print("Starting program")
    main()

