# soundcloud explorer
Plays the most commented 10 seconds of a random song on SoundCloud and adds it to a playlist if you like it

## This script uses undocumented soundcloud APIs (since you cannot currently ask for an api key). Use it at your own risk! (theoretically your soundcloud account might get banned)
## NOT FINISHED, UNDER DEVELOPMENT
- TODO: possibility to chose a playlist instead of creating a new one everytime (easy, functions already implemented)
- TODO: debug mode to output more stuff
- TODO: massive refactor (this code is a prototype, I basically copy-pasted from the jupyther notebook that I was using to test things quickly)
- TODO: explore different genres (currently hardcoded) (easy)
- TODO: explore songs of a given playlist or artist or another user or similar artists to a given one?
- TODO: develop an actual algorithm to suggest better songs based on previously liked ones? (idk)
- TODO: GUI?
- TODO: requirements.txt

## Credits
Idea taken from https://twitter.com/yush_g (https://github.com/Divide-By-0/ideas-for-projects-people-would-use)

## Required libs
- simpleaudio (https://simpleaudio.readthedocs.io/en/latest/)
- pydub (https://github.com/jiaaro/pydub)

## How to use
- Currently a new playlist will be created everytime you run the program (no risk of deleting my playlists by accident ahah)
- Get your client_id from soundcloud (you can use the developer console from any browser) and save it in a file named client_id (located in the same directory as the python script).
- Get your OAuth id from soundcloud (you can use the developer console from any browser) and save it in a file named oauth (located in the same directory as the python script).

```console
$> python3 sc-explorer.py
[*] Buffering song queue for 5 seconds...
[*] Exploring 200 songs
[*] Starting program
Playlist name: TestPlaylist
[*] Created empty private playlist "TestPlaylist"
[+] Playing: "Noir and Haze - Around (Solomun Vox) 128kbit - Noir Music" (starting from 0 seconds)
Do you like it? [y/n/nq/yq] n
[+] Playing: "Josh Butler - Got A Feeling (Bontan Remix / Pleasurekraft Edit)" (starting from 21 seconds)
Do you like it? [y/n/nq/yq] yq
[+] Adding songs to the playlist "TestPlaylist"
[*] Added 1 songs to the playlist
Press ctrl+c to force close the queue filling thread (TODO: quit automatically)
```
