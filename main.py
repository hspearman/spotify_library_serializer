import uuid
import constants
import json
from flask import Flask, session
from api import api
import logging
from logging.handlers import SMTPHandler


app = Flask(__name__)
app.register_blueprint(api)


#
# Generates a CSRF token to protect against un-authorized requests
#
def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = str(uuid.uuid4())
    return session['_csrf_token']


#
# Enables logging that sends error reports to admins
#
def enable_logging():
    if not app.debug:
        mail_handler = SMTPHandler(
            mailhost=(constants.SMTP_SERVER, constants.SMTP_PORT),
            fromaddr=constants.SMTP_EMAIL,
            toaddrs=constants.ADMIN,
            subject='Your Application Failed',
            credentials=(constants.SMTP_EMAIL, constants.SMTP_PASSWORD),
            secure=())
        mail_handler.setLevel(logging.ERROR)
        logging.getLogger().addHandler(mail_handler)


#
# Loads config values for app from file
#
def load_config(flask_app):

    try:

        # Read config file
        config_file = open(constants.CONFIG_FILENAME)
        config_file_contents = config_file.read()

        # Initialize config via file
        config = json.loads(config_file_contents)
        constants.init(config)

        flask_app.secret_key = config["secret_key"]

    except:
        return


if __name__ == '__main__':

    load_config(app)
    enable_logging()
    app.jinja_env.globals['csrf_token'] = generate_csrf_token
    app.run()

