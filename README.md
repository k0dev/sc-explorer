# sc-explorer
<<<<<<< HEAD
Plays the most commented 10 seconds of a random song on SoundCloud and adds it to a playlist if you like it
=======
Plays the most commented 10 seconds of a random song on SoundCloud® and adds it to a playlist if you like it
>>>>>>> e946c7d (update README.md)

## This script uses undocumented SoundCloud® APIs (since you cannot currently ask for an api key). Use it at your own risk! (theoretically your account might get banned)
## NOT PRODUCTION READY YET (RUN IT ONLY LOCALLY)
## TODO
- TODO: massive refactor (this code is a prototype, I basically copy-pasted from the jupyther notebook that I was using to test things quickly)
- TODO: explore different playlists (currently hardcoded) (easy)
- TODO: explore songs of a given playlist or artist or another user or similar artists to a given one?
- TODO: develop an actual algorithm to suggest better songs based on previously liked ones? (idk)
- TODO: better gui lol

## Credits
Idea taken from https://twitter.com/yush_g (https://github.com/Divide-By-0/ideas-for-projects-people-would-use)

## Installation
```console
$ pip install -r requirements.txt
$ echo YOUR_CLIENT_ID > client_id
$ echo YOUR_OAUTH_TOKEN > oauth
$ flask --app sc-explorer run --debug
```
