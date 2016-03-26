import constants
import json
from flask import Flask
from api import api

app = Flask(__name__)
app.register_blueprint(api)


#
# Loads config values for app from file
#
def load_config(flask_app):

    try:

        # Read config file
        config_file = open(constants.CONFIG_FILENAME)
        config_file_contents = config_file.read()

        # Deserialize file contents via JSON
        config = json.loads(config_file_contents)

        # Set config variables
        constants.init({
            'CLIENT_ID': config["client_id"],
            'CLIENT_SECRET': config["client_secret"],
            'REDIRECT_URI': config["redirect_uri"],
            'AUTHORIZE_ENDPOINT': config["authorize_endpoint"],
            'TOKEN_ENDPOINT': config["token_endpoint"],
            'TRACKS_ENDPOINT': config["tracks_endpoint"]
        })

        flask_app.secret_key = config["secret_key"]

    except:
        return


if __name__ == '__main__':

    load_config(app)
    app.run()

