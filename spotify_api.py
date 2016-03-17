import json
import requests


# Standardize private variables
_TRACK_LIMIT_TOTAL = 100;
_TRACK_LIMIT_PER_CALL = 50
_TRACK_LIMIT = 25
_TRACKS_PER_PAGE = 25

REDIRECT_URI = 'http://localhost:8000/spotify/authorize'

# API endpoints
_TOKEN_ENDPOINT = 'https://accounts.spotify.com/api/token'
_GET_TRACKS_ENDPOINT = 'https://api.spotify.com/v1/me/tracks'

# oAuth information
_CLIENT_ID = '04339da82c884355a79da568a4dfcddf'
_CLIENT_SECRET = 'c0dc2e1bf7d24967a49dde6c8078a448'


def authorize_user():
    payload = {
        'client_id': _CLIENT_ID,
        'client_secret': _CLIENT_SECRET,
        # 'code': request.query_params.get('code', None),
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(_TOKEN_ENDPOINT, data=payload)

    # Store token and timestamp in session
    token = json.loads(response.text)


def get_tracks_paged(token, offset):

    assert token, "Cannot get paged track results from Spotify: token not found!"
    response = requests.get(_GET_TRACKS_ENDPOINT,
        headers={
            'Authorization': 'Bearer {}'.format(token['access_token'])
        },
        params={
            'limit': _TRACK_LIMIT,
            'offset': offset
        })

    tracks = json.loads(response.text)
    return tracks
