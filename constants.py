# General
ADMIN = ''
SMTP_SERVER = ''
SMTP_PORT = -1
SMTP_EMAIL = ''
SMTP_PASSWORD = ''
CONFIG_FILENAME = 'config.json'

# API endpoints
AUTHORIZE_ENDPOINT = ''
TOKEN_ENDPOINT = ''
TRACKS_ENDPOINT = ''

# Spotify API info
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = ''
TRACKS_PER_PAGE = 50
TRACK_LIMIT_TOTAL = -1
MAX_API_ATTEMPTS = 3


def init(config):

    global ADMIN, \
        SMTP_SERVER, \
        SMTP_PORT, \
        SMTP_EMAIL, \
        SMTP_PASSWORD, \
        CLIENT_ID, \
        CLIENT_SECRET, \
        REDIRECT_URI, \
        AUTHORIZE_ENDPOINT, \
        TOKEN_ENDPOINT, \
        TRACKS_ENDPOINT

    ADMIN = config["admin"]
    SMTP_SERVER = config["smtp_server"]
    SMTP_PORT = config["smtp_port"]
    SMTP_EMAIL = config["smtp_email"]
    SMTP_PASSWORD = config["smtp_password"]
    CLIENT_ID = config["client_id"]
    CLIENT_SECRET = config["client_secret"]
    REDIRECT_URI = config["redirect_uri"]
    AUTHORIZE_ENDPOINT = config["authorize_endpoint"]
    TOKEN_ENDPOINT = config["token_endpoint"]
    TRACKS_ENDPOINT = config["tracks_endpoint"]
