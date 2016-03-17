import urllib
import  json
from datetime import datetime

import flask
import requests
from flask import Flask, render_template, redirect, request, session

app = Flask(__name__)

# General
_CONFIG_FILENAME = 'config.json'
_TRACKS_PER_PAGE = 50
_TRACK_LIMIT_TOTAL = -1
_MAX_API_ATTEMPTS = 3

# API endpoints
_AUTHORIZE_ENDPOINT = ''
_TOKEN_ENDPOINT = ''
_TRACKS_ENDPOINT = ''

# Spotify API info
_CLIENT_ID = ''
_CLIENT_SECRET = ''
_REDIRECT_URI = ''


#
# Checks if user is authorized via access token
#
def is_user_authorized():

    is_authorized = False

    # Check if token exists
    if "access_token" in session:

        # Check if token expired
        is_expired = datetime.now - session["authorization_timestamp"] < session["expires_in"]
        if not is_expired:
            is_authorized = True

    return is_authorized


#
# Selects template to render for site's default URL
#
@app.route('/')
def index():

    # Decide on template to render
    template = 'index.html'
    if is_user_authorized():
        template = 'index_authorized.html'

    return render_template(template)


#
# Redirects user to authorize spotify for app
#
@app.route('/authorize')
def authorize():

    # TODO: Include state to protect against CSRF
    # Build query params
    query_string = urllib.parse.urlencode({
        'client_id': _CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': _REDIRECT_URI,
        'scope': 'user-library-read'
    })

    # Build url
    spotify_url = ''.join([
        _AUTHORIZE_ENDPOINT,
        '?',
        query_string
    ])

    # Redirect user to spotify authorize page
    return redirect(spotify_url)


#
# Acts as callback for spotify's authorization workflow
# When called, exchanges code for access token
#
@app.route('/login')
def login():

    # TODO: Handle error
    # Check for errors
    if request.args.get('error'):
        return

    # TODO: Handle error
    # Try to get code
    code = request.args.get('code')
    if not code:
        return

    # Try to get token w/ code
    try:
        # Store timestamp of when tokens fetched
        session["authorization_timestamp"] = datetime.now()

        # Fetch tokens via Spotify
        response = requests.post(
            _TOKEN_ENDPOINT,
            data={
                'client_id': _CLIENT_ID,
                'client_secret': _CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': _REDIRECT_URI
            })

        # Deserialize response
        response_obj = response.json()

        # Store tokens from response
        session["access_token"] = response_obj["access_token"]
        session["refresh_token"] = response_obj["refresh_token"]
        session["expires_in"] = response_obj["expires_in"]

    # Handle failure
    except Exception:
        return

    return render_template('index_authorized.html')


#
# Get user's spotify library
#
@app.route('/library')
def get_library():
    tracks = get_tracks()
    return flask.jsonify({'tracks': tracks})


#
# Get all tracks from user's Spotify library
#
def get_tracks():

    # Loop through user's tracks
    all_tracks = []
    next_page = None
    end_of_results = False
    while not end_of_results:

        # Get page of tracks
        results = get_tracks_paged(
            _TRACKS_PER_PAGE,
            next_page)

        # Add page of tracks
        tracks = results['items']
        all_tracks.extend(tracks)

        # Check if reached end of user's library
        next_page = results['next']
        end_of_results = next_page is None

    return all_tracks


#
# Get a page of tracks from user's Spotify library
#
def get_tracks_paged(
        limit,
        page_url,
        num_of_tries=0):

    # Stop if max tries exceeded
    if num_of_tries >= _MAX_API_ATTEMPTS:
        return None

    # Get page of tracks
    result = get_tracks_paged_internal(
        limit,
        page_url)

    # If bad gateway ...
    is_bad_gateway = 'error' in result \
        and 'status' in result['error'] \
        and result['error']['status'] == 502
    if is_bad_gateway:

        # Try again
        # (Sometimes Spotify gives random 502 errors)
        num_of_tries += 1
        result = get_tracks_paged(
            limit,
            page_url,
            num_of_tries)

    return result


def get_tracks_paged_internal(
        limit,
        page_url):

    # Make sure access token exists
    assert \
        session['access_token'],\
        "Cannot get paged track results from Spotify: token not found!"

    # Get page of tracks
    url = page_url if page_url else _TRACKS_ENDPOINT
    response = requests.get(
        url,
        headers={
            'Authorization': 'Bearer {}'.format(session['access_token'])
        },
        params={
            'limit': limit
        })

    # Return page of tracks
    tracks = json.loads(response.text)
    return tracks


#
# Loads config values for app from file
#
def load_config(flask_app):

    try:
        # Read config file
        config_file = open(_CONFIG_FILENAME)
        config_file_contents = config_file.read()

        # Get access to global constants
        global _CLIENT_ID,\
            _CLIENT_SECRET,\
            _REDIRECT_URI,\
            _AUTHORIZE_ENDPOINT,\
            _TOKEN_ENDPOINT, \
            _TRACKS_ENDPOINT

        # Deserialize file contents via JSON
        config = json.loads(config_file_contents)

        # Set config variables
        _CLIENT_ID = config["client_id"]
        _CLIENT_SECRET = config["client_secret"]
        _REDIRECT_URI = config["redirect_uri"]
        _AUTHORIZE_ENDPOINT = config["authorize_endpoint"]
        _TOKEN_ENDPOINT = config["token_endpoint"]
        _TRACKS_ENDPOINT = config["tracks_endpoint"]
        flask_app.secret_key = config["secret_key"]
    # TODO: Handle error
    except:
        return

if __name__ == '__main__':

    load_config(app)
    app.run()

