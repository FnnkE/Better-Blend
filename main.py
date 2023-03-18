from dotenv import load_dotenv
import os
import spotipy

load_dotenv()
clientID = os.getenv("CLIENT_ID")
clientSecret = os.getenv("CLIENT_SECRET")

#Limit Scope
scope = "ugc-image-upload, user-read-playback-state, user-modify-playback-state, user-read-currently-playing, app-remote-control, streaming, playlist-read-private, playlist-read-collaborative, playlist-modify-private, playlist-modify-public, user-follow-modify, user-follow-read, user-read-playback-position, user-top-read, user-read-recently-played, user-library-modify, user-library-read, user-read-email, user-read-private"

token1 = spotipy.util.prompt_for_user_token(scope=scope,client_id=clientID,client_secret=clientSecret,redirect_uri='http://fnke-better-blend.com/')
token2 = spotipy.util.prompt_for_user_token(scope=scope,client_id=clientID,client_secret=clientSecret,redirect_uri='http://fnke-better-blend.com/')
sp = spotipy.Spotify(auth=token1)
#sp2 = spotipy.Spotify(auth=token2)


#Functions


#Get most played songs from user over the past month
#Returns list of song URIs
def getTopTracks():
    return sp.current_user_top_tracks(limit=50, time_range="short_term")['items']

#Get all playlists from user
#Returns list of playlist IDs
def getPlaylists():
    flag = True
    playlists = []
    offset = 0
    while flag:
        newPlaylists = sp.current_user_playlists(limit=50, offset=offset)['items']
        if (len(newPlaylists)!=50):
            flag = False
        offset += 50
        playlists.extend(newPlaylists)
        print("Getting playlists: ", offset)
    return playlists

#Get all songs from a playlist given the ID
#Returns list of song URIs
def getPlaylistSongs(playlistID):
    flag = True
    songs = []
    offset = 0
    while flag:
        tracks = sp.playlist_tracks(playlistID, limit=100, offset=offset)['items']
        if (len(tracks)!=100):
            flag = False
        offset += 100
        songs.extend(tracks)
    return songs
    
#Create a playlist with a specified title and description given a username
#Returns playlist ID
def createPlaylist(srcUsr, usr2):
    return sp.user_playlist_create(srcUsr, f'</> {srcUsr} + {usr2}', public=True, collaborative=False, description=f'A Better Together | https://github.com/FnnkE/Better-Blend <BB{srcUsr[0]}{usr2[0]}/> ')['id']

#Adds songs to a playlist given the playlist ID and song URIs
#Returns nothing
def addSongs(playlistID, uris):
    inRange = True
    offset = 0
    range = len(uris)
    while inRange:
        limit = offset + 100
        if limit > range:
            limit = range
        sp.playlist_add_items(playlistID, uris[offset:limit])
        print("adding songs", offset, limit)
        offset += 100
        if offset > range:
            inRange = False

#Removes all songs from a given playlist
#Returns nothing
def removeSongs(playlistID):
    songs = getPlaylistSongs(playlistID=playlistID)
    uris = []
    for idx, song in enumerate(songs):
        if idx%50 == 0 and idx != 0:
            print("Progress: ", idx)
            sp.playlist_remove_all_occurrences_of_items(playlistID, uris)
            uris = []
        newSong = song['track']['uri']
        uris.append(newSong)
    if len(uris) != 0:
        sp.playlist_remove_all_occurrences_of_items(playlistID, uris)

#Checks through playlists from a given user to find if a playlist already exists
#Returns playlist ID
def checkPlaylists(srcUsr, usr2, playlists):
    playlistMade = False
    for playlist in playlists:
        if f'&lt;BB{srcUsr[0]}{usr2[0]}&#x2F;&gt;' in playlist['description'] or f'&lt;BB{usr2[0]}{srcUsr[0]}&#x2F;&gt;' in playlist['description']: #Checks if <BB/> exists in the description
            playlistMade = True
            newPlaylistID = playlist['id']
            print(f'Found Playlist...{newPlaylistID}')
            removeSongs(newPlaylistID)
    if not playlistMade:
        newPlaylistID = createPlaylist(srcUsr, usr2)
        print(f'Creating New Playlist... {newPlaylistID}')
    return newPlaylistID


#Body


#Get tokens from both users
username1 = sp.current_user()['id']
username2 = sp.current_user()['id']

#Get top songs from both users
topUser1 = getTopTracks()
topUser2 = getTopTracks()

#Get all playlists from both users to find old playlist
playlistsUser1 = getPlaylists()
playlistsUser2 = getPlaylists()
print("Data received...")

#Check if playlist already exits. If not, create one
bbUser1 = checkPlaylists(username1, username2, playlistsUser1)
bbUser2 = checkPlaylists(username2, username1, playlistsUser2)

#Combine a mix of song URIs from top tracks from both users
uris = []
for i in range(50):
    if (len(uris) == 50):
        break
    else:
        newSong = topUser1[i]['uri']
        if newSong not in uris:
            uris.append(newSong)
        if (len(uris) == 50):
            break
        newSong = topUser2[i]['uri']
        if newSong not in uris:
            uris.append(newSong)
print("URIs gathered...")

#Add songs into playlist
addSongs(bbUser1, uris)
addSongs(bbUser2, uris)
print("DONE!")
