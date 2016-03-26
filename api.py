import json
from flask import render_template, redirect, Response, Blueprint
from spotify_utility import build_authorization_url, refresh_token, is_token_existent, is_token_expired, get_token, \
    get_tracks


api = Blueprint('api', __name__)


#
# Selects template to render for site's default URL
#
@api.route('/')
def index():

    template = 'index.html'

    # If token exists ...
    if is_token_existent():

        # If token expired, try to refresh
        if is_token_expired():
            try:
                refresh_token()
            # If refresh fails, fall-back on default template
            except:
                pass

        # Otherwise, select authorized template
        else:
            template = 'index_authorized.html'

    return render_template(template)


#
# Redirects user to spotify authorization endpoint
#
@api.route('/authorize')
def authorize():
    # Redirect user to spotify authorize page
    spotify_url = build_authorization_url()
    return redirect(spotify_url)


#
# Acts as callback for spotify's authorization workflow
# When called, exchanges code for access token
#
@api.route('/login')
def login():
    try:
        get_token()
    # Ignore failure (workflow restarts on redirect)
    except:
        pass

    return redirect("/")


#
# Get user's spotify library
#
@api.route('/library')
def get_library():

    # Try to get user's tracks
    try:

        tracks = get_tracks()
        return Response(
            json.dumps(tracks),
            headers={
                'Content-Disposition': 'attachment;filename=library.json',
                'Content-Type': 'application/json'
            })

    # On error, redirect to index
    except:
        return redirect("/")
