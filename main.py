from dotenv import load_dotenv
import os
import base64
from requests import post, get, delete
import json

load_dotenv()

clientID = os.getenv("CLIENT_ID")
clientSecret = os.getenv("CLIENT_SECRET")
TOKEN = os.getenv("TOKEN")

def getToken():
    authString = clientID + ":" + clientSecret
    authBytes = authString.encode("utf-8")
    authBase64 = str(base64.b64encode(authBytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + authBase64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    jsonResult = json.loads(result.content)
    token = jsonResult["access_token"]
    return token

def getAuthHeader(token):
    return {"Authorization": "Bearer " + token}

def getTopTracks(token):
    url = "https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=50"
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
        }
    result = get(url,headers=headers)
    jsonResult = json.loads(result.content)["items"]
    return jsonResult
    
def createPlaylist(token, username):
    url = f"https://api.spotify.com/v1/users/{username}/playlists"
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
        }
    data = {
        "name": "Better Blend™",
        "description": "better together or something | github link",
        "public": "true"
        }
    result = post(url, headers=headers, data=json.dumps(data))
    print(result)
    return json.loads(result.content)['id']

def addSongs(playlistID, uris, token):
    url = f"https://api.spotify.com/v1/playlists/{playlistID}/tracks?uris=" + uris
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
        }
    result = post(url, headers=headers)
    return result

def removeSongs(playlistID, token, songs):
    url = f"https://api.spotify.com/v1/playlists/{playlistID}/tracks"
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
        }
    data = '{"tracks":['
    index = 1
    for song in songs:
        index += 1
        data += '{"uri":"'+ song['track']['uri'] + '"},'
    data = data[:-1] + "]}"
    result = delete(url, headers=headers, data=data)
    return result

#Get tokens from both users
token1 = TOKEN#getToken()
username1 = 'nerd-e'
#token2 = getToken()
print("Tokens created...")


#Get top songs from both users
topUser1 = getTopTracks(token1)
#topUser2 = getTopTracks(token2)
print("Top tracks received...")


#Create new playlist    -    If already exists
newPlaylistID = createPlaylist(token1, username1)
#newPlaylistID2 = createPlaylist(token2)    - Create two playlists?
print("New playlist created...")



#Combine into one array and string
uris = ''
songs=[]

#are commas needed?
for i in range(50):
    if (len(songs) == 50):
        break
    else:
        newSong = topUser1[i]['uri']
        if newSong not in songs:
            songs.append(newSong)
            uris += newSong + ','
        """
        if (len(songs) == 50):
            break
        newSong = topUser2[i]['id']
        if newSong not in songs:
            songs.append(newSong)
            ids += newSong + ','
        """
uris = uris[:-1] #remove comma
print("IDs gathered...")


#Add songs into playlist
addSongs(newPlaylistID, uris, token1)
print("DONE!")
