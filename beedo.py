# coding=utf-8
from __future__ import absolute_import

import os

from flask import Flask, current_app, request, g
from flask.json import JSONEncoder

from utils.request import get_remote_addr, get_request_url

from loaders import load_config, load_files, load_keys
from analyzer import SimpleAnalyzer
from blueprints import register_blueprints


__version_info__ = ('0', '0', '1')
__version__ = '.'.join(__version_info__)


# create app
app = Flask(__name__)
app.version = __version__

load_config(app)

# make importable for plugin folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# init app
app.debug = app.config.get('DEBUG', True)

# encoder
app.json_encoder = JSONEncoder

# register blueprints
register_blueprints(app)

# data
DATA = dict()
DATA['files'] = load_files(app)
DATA['keys'] = load_keys(DATA['files'])


@app.before_request
def app_before_request():
    if app.debug:
        DATA['files'] = load_files(current_app)
        DATA['keys'] = load_keys(DATA['files'])

    g.keys = DATA['keys']
    g.files = DATA['files']

    g.request_remote_addr = get_remote_addr()
    g.request_path = request.path


if __name__ == '__main__':
    host = app.config.get('HOST')
    port = app.config.get('PORT')

    print "-------------------------------------------------------"
    print 'Pyco: {}'.format(app.version)
    print "-------------------------------------------------------"

    if app.debug:
        print('Pyco is running in DEBUG mode !!!')
        print('Jinja2 template folder is about to reload.')

    app.run(host=host, port=port, debug=True, threaded=True)