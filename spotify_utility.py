import json
import logging
import urllib
from datetime import datetime
import requests
from flask import session, request
import constants


def build_authorization_url():
    # Build query params
    query_string = urllib.parse.urlencode({
        'client_id': constants.CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': constants.REDIRECT_URI,
        'scope': 'user-library-read'
    })

    # Build url
    spotify_url = ''.join([
        constants.AUTHORIZE_ENDPOINT,
        '?',
        query_string
    ])

    return spotify_url


#
# Refreshes a token against Spotify API
#
def refresh_token():

    # Refresh token
    response = requests.post(
        constants.TOKEN_ENDPOINT,
        auth=(constants.CLIENT_ID, constants.CLIENT_SECRET),
        data={
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token']
        })

    # Store fresh access token in session
    response_obj = response.json()
    session['access_token'] = response_obj['access_token']


def get_token():
    code = request.args.get('code')

    # Store timestamp of when tokens fetched
    session["authorization_timestamp"] = datetime.now()

    # Fetch tokens via Spotify
    response = requests.post(
        constants.TOKEN_ENDPOINT,
        data={
            'client_id': constants.CLIENT_ID,
            'client_secret': constants.CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': constants.REDIRECT_URI
        })

    # Deserialize response
    response_obj = response.json()

    # Store tokens from response
    session["access_token"] = response_obj["access_token"]
    session["refresh_token"] = response_obj["refresh_token"]
    session["expires_in"] = response_obj["expires_in"]


#
# Checks if user is authorized via access token
#
def is_token_expired():

    is_expired = False

    # Check if token exists
    if is_token_existent():

        # Check if token expired
        time_lapsed = (datetime.now() - session["authorization_timestamp"]).total_seconds()
        is_expired = time_lapsed >= session["expires_in"]

    return is_expired


#
# Check if access token exists in user's session
#
def is_token_existent():
    return "access_token" in session


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
        try:
            results = get_tracks_paged(
                constants.TRACKS_PER_PAGE,
                next_page)
        # Log error on failure
        except:
            logging.getLogger().error(
                'Failed to get user\'s tracks',
                exc_info=True)

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
    if num_of_tries >= constants.MAX_API_ATTEMPTS:
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


#
# Handles internal logic for getting page of tracks
#
def get_tracks_paged_internal(
        limit,
        page_url):

    # Make sure access token exists
    assert \
        session['access_token'],\
        "Cannot get paged track results from Spotify: token not found!"

    # Get page of tracks
    url = page_url if page_url else constants.TRACKS_ENDPOINT
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
