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
with open('oauth', 'r') as f:      # ! Place your oauth code in a file named oauth (same directory)
    oauth = f.read().strip()

api_url = 'https://api-v2.soundcloud.com'
search_endpoint = '/search/tracks'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
}

authenticated_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Authorization': 'OAuth ' + oauth
}

song_window_queue = queue.Queue(maxsize=3)

# TODO: proper debug output

def create_empty_private_playlist(title):
    url = api_url + '/playlists?client_id=' + client_id
    body = {'playlist':{"title": title,"sharing":"private","tracks":[],"_resource_type":"playlist"}}
    r = requests.post(url, headers=authenticated_headers, json=body)
    assert r.status_code == 201
    print('[*] Created empty private playlist "' + title + '"')
    return str(r.json()['id'])

def add_songs_to_playlist(playlist_id, song_list):
    url = api_url + '/playlists/' + playlist_id + '?client_id='+ client_id
    body = {"playlist":{"tracks":song_list}}
    r = requests.put(url, headers=authenticated_headers, json=body)
    assert r.status_code == 200
    print('[*] Added ' + str(len(song_list)) + ' songs to the playlist')

# TODO: pagination
def search_by_genre(genre, query="*"): # TODO: more filtering... what if a song has 0 comments? or has too few likes? we can filter on those!!
    request_url = api_url + search_endpoint + "?q=" + query + "&filter.genre=" + genre + "&sort=popular&client_id=" + client_id + "&locale=en&limit=200"
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
    print('[*] Exploring ' + str(len(candidates)) + ' songs')
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
        song_window_queue.put({'title': song_title, 'window': song_window, 'id': song_id, 'window_position': window_position}, block=True) # TODO: non blocking so the thread can actually exit 
        #print('[*] "' + song_title + '"   inserted into queue')

# TODO: maybe the user has more than 50 playlists
def get_user_owned_playlists():
    url = api_url + '/me/library/all?client_id=' + client_id + '&limit=50&offset=0'
    r = requests.get(url, headers=authenticated_headers)
    assert r.status_code == 200
    library = r.json()['collection']
    library = filter(lambda item: item['type'] == 'playlist', library)
    return [{'playlist_title': item['playlist']['title'], 'playlist_id': str(item['playlist']['id'])} for item in library]

def main():
    name = input('Playlist name: ')
    playlist_id = create_empty_private_playlist(name)
    song_ids = []
    running = True
    while running:
        song = song_window_queue.get()
        print('[+] Playing: "' + song['title'] + '" (starting from ' + str(song['window_position']) + ' seconds)')
        play(song['window'])
        choice = input("Do you like it? [y/n/nq/yq] ")
        if choice == 'y':
            song_ids.append(song['id'])
        elif choice == 'nq':
            break
        elif choice == 'yq':
            song_ids.append(song['id'])
            break
        else:
            continue
    print('[+] Adding songs to the playlist "' + name + '"')
    add_songs_to_playlist(playlist_id, song_ids)

if __name__ == "__main__":
    t = threading.Thread(target=fill_song_queue_loop, args=('deephouse',))
    t.start()
    print("[*] Buffering song queue for 5 seconds...")
    time.sleep(5)
    print("[*] Starting program")
    main()
    print("Press ctrl+c to force close the queue filling thread (TODO: quit automatically)") # TODO: !!!!
