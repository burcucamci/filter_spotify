from spotipy import Spotify
from spotipy.util import prompt_for_user_token
import spotipy.util as util
from flask import Flask, render_template, request
from webbrowser import open as wbopen
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

# Initialise globals
app = Flask(__name__)
username = ""
artistList = []
genreList = []
sp = Spotify

# Open browser
wbopen('http://127.0.0.1:5000/')
#Login
@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # Get username 
        global username, sp
        username = request.form["usernameInput"]

        # Authorisation
        token = prompt_for_user_token(username='username',
                                      scope='playlist-read-private user-top-read user-library-read playlist-modify-private playlist-modify-public',
                                      client_id='...',
                                      client_secret='...',
                            
                                      redirect_uri='http://localhost:8080')
        sp = Spotify(auth=token)

        return render_template("create.html")
    else:
        return render_template("index.html")

#Playlist create
@app.route("/create/", methods=["POST", "GET"])
def create():
    if request.method == "GET":
        # Set playlist settings
        playlistName = request.form["playlistName"]
        playlistDescription = request.form["playlistDescription"]
        privacyInput = request.form["privacy"]
        
        if privacyInput == "Public":
            privacy = True
        else:
            privacy = False

        # Create playlist
        
        sp.user_playlist_create(user=username, name=playlistName, public=privacy,
                                description=playlistDescription)
        return render_template("preferences.html")
    else:
        return render_template("preferences.html")

#Preferences 
@app.route("/preferences/", methods=["POST", "GET"])
def preferences():
    if request.method == "POST":
        global artistList, genreList
        # Get user suggestions
        artistsString = request.form["artists"]
        genresString = request.form["genres"]

        # Update artists
        artistsSplit = artistsString.split(",")
        if len(artistsSplit) < 3:
            artistsAdded = len(artistsSplit)
        else:
            artistsAdded = 3
        for i in range(artistsAdded):
            artist = artistsSplit[i]
            artistCode = sp.search(artist, limit=1, type='artist', market="AU")['artists']['items'][0]['uri']
            artistList.append(artistCode)

        # Update genres
        genresSplit = genresString.split(",")
        if len(genresSplit) > 2:
            if artistsAdded == 3:
                genresAdded = 2
            else:
                genresAdded = 3
        else:
            genresAdded = len(genresSplit)
        for i in range(genresAdded):
            genre = genresSplit[i]
            genreList.append(genre)
        return render_template("filters.html")
    else:
        return render_template("preferences.html")

#Filters
@app.route("/filters/", methods=["POST", "GET"])
def filters():
    if request.method == "POST":
        # Get user inputs
        valence = request.form["valence"]
        popularity = request.form["popularity"]

        # Set valence settings(Mood)
        minValence = float(0)
        maxValence = float(1)
        if valence == "Happy Music":
            minValence = float(0.75)
        elif valence == "Sad Music":
            maxValence = float(0.25)

        # Set popularity settings
        minPopularity = 0
        maxPopularity = 100
        if popularity == "Popular Music":
            minPopularity = 75
        elif popularity == "Unpopular Music":
            maxPopularity = 25

        # Get recommended tracks 
        recommendations = sp.recommendations(seed_artists=artistList, seed_genres=genreList, limit=50,
                                             country="TR", min_valence=float(minValence), max_valence=float(maxValence),
                                             min_popularity=minPopularity,
                                             max_popularity=maxPopularity)['tracks']
        trackList = []
        #append add playlist
        for recommendedTrack in range(len(recommendations)):
            trackList.append(recommendations[recommendedTrack]['uri'])

        # Get playlist URI
        playlistCode = sp.current_user_playlists(limit=1)['items'][0]['uri']

        # Get playlist embed code
        uriSplit = playlistCode.split("playlist:")
        uriEmbed = uriSplit[1]
        embedCode = "https://open.spotify.com/embed/playlist/" + uriEmbed

        # Add tracks to playlist
        sp.user_playlist_add_tracks(username, playlist_id=playlistCode, tracks=trackList)

        # Open playlist
        wbopen(playlistCode)
        return render_template("success.html", embedCode=embedCode)
    else:
        return render_template("filters.html")
#success
@app.route("/success/", methods=["POST", "GET"])
def success():
    if request.method == "POST":
        # Reset globals
        global artistList, genreList
        artistList = []
        genreList = []
        return render_template("create.html")
    else:
        return render_template("success.html")

if __name__ == "__main__":
    app.run(debug=True)
