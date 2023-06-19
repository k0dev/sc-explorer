# soundcloud explorer
Plays the most commented 10 seconds of a random song on SoundCloud and adds it to a playlist if you like it
## This script uses undocumented soundcloud APIs (since you cannot currently ask for an api key). Use it at your own risk! (your soundcloud account might get banned)
## NOT FINISHED, UNDER DEVELOPMENT
- TODO: massive refactor (this code is a prototype, I basically copy-pasted from the jupyther notebook that I was using to test things quickly)
- TODO: explore different genres (currently hiphop-rap is hardcoded) (easy)
- TODO: explore songs of a given playlist or artist or another user or similar artists to a given one?
- TODO: actually add liked songs to a playlist (easy)
- TODO: develop an actual algorithm to suggest better songs based on previously liked ones? (idk)
- TODO: GUI?
- TODO: requirements.txt

Idea taken from https://twitter.com/yush_g (https://github.com/Divide-By-0/ideas-for-projects-people-would-use)

## Required libs
- simpleaudio (https://simpleaudio.readthedocs.io/en/latest/)
- pydub (https://github.com/jiaaro/pydub)

## How to use
Get your client_id from soundcloud (you can use the developer console from any browser) and save it in a file named client_id (located in the same directory as the python script).
```console
$> python3 sc-explorer.py
```
