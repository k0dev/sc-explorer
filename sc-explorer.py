import json
import requests

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

with open('client_id', 'r') as f:
    client_id = f.read().strip()
with open('oauth', 'r') as f:
    oauth = f.read().strip()

api_url = 'https://api-v2.soundcloud.com'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
}

authenticated_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Authorization': 'OAuth ' + oauth
}


def most_commented_window_position(client_id, track_id, comments_per_request, time_window_size_sec, max_comments):
    url = 'https://api-widget.soundcloud.com/resolve?url=https://api.soundcloud.com/tracks/'+track_id+'&format=json&client_id='+client_id
    r = requests.get(url, headers=headers)
    assert r.status_code == 200
    response = r.json()
    commentable = response['commentable']
    comments_count = response['comment_count']
    track_duration_ms = response['duration']
    track_duration_sec = response['duration'] // 1000
    
    if not commentable or track_duration_sec < 20 or track_duration_sec > 300 or response['media']['transcodings'][0]['snipped']: # TODO: handle this better
        return -1

    comments_count = min(max_comments, comments_count)
    timeline = [0]*(track_duration_sec + 1)
    for offset in range(0, comments_count, comments_per_request):
        comment_url = api_url+'/tracks/'+track_id+'/comments?threaded=0&client_id=' + client_id + '&limit='+str(comments_per_request)+'&offset='+str(offset)
        r = requests.get(comment_url, headers=headers)
        assert r.status_code == 200
        response = r.json()['collection']
        for comment in response:
            if comment['timestamp'] is None or comment['timestamp'] > track_duration_ms or comment['timestamp']//1000 == 0:
                #print("[-] skipping comment: no timestamp or wrong timestamp?")
                continue
            else:
                timeline[comment['timestamp']//1000] += 1
    
    max_comments = sum(timeline[:time_window_size_sec])
    time_window_position = 0
    current_comments = max_comments
    for i in range(time_window_size_sec, track_duration_sec+1):
        current_comments += timeline[i]
        current_comments -= timeline[i-time_window_size_sec]
        if (current_comments > max_comments):
            max_comments = current_comments
            time_window_position = i-time_window_size_sec+1
        
    return time_window_position*1000

def create_empty_public_playlist(title):
    url = api_url + '/playlists?client_id=' + client_id
    body = {'playlist':{"title": title,"sharing":"public","tracks":[],"_resource_type":"playlist"}}
    r = requests.post(url, headers=authenticated_headers, json=body)
    assert r.status_code == 201
    print('[*] Created empty public playlist "' + title + '"')
    return str(r.json()['id'])

def add_songs_to_playlist(playlist_id, song_list):
    url = api_url + '/playlists/' + playlist_id + '?client_id='+ client_id
    body = {"playlist":{"tracks":song_list}}
    r = requests.put(url, headers=authenticated_headers, json=body)
    assert r.status_code == 200
    print('[*] Added ' + str(len(song_list)) + ' songs to the playlist')
    return r.json()['permalink_url']


@app.route('/')
def page_index():
    return render_template('index.html')

@app.route('/most_commented_window_position', methods=['POST'])
def page_most_commented_window_position():
    if request.method == 'POST':
        song_id = request.form.get('song_id')
        if song_id is None:
            return jsonify({'position': -1})
        position = most_commented_window_position(client_id, song_id, 1000, 10, 1000)
        return jsonify({'position': position})

@app.route('/add_songs_to_playlist', methods=['POST'])
def page_add_songs_to_playlist():
    if request.method == 'POST':
        songs = json.loads(request.form.get('songs'))
        if songs is None:
            return 'Error'
        playlist_id = create_empty_public_playlist('sc-explorer-playlist')
        playlist_url = add_songs_to_playlist(playlist_id, songs)
        if playlist_url == None:
            return "Error"
        return 'Playlist created <a href="' + playlist_url + '">HERE</a>'
