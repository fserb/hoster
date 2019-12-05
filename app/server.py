#!/usr/bin/env python3

"""
 To run locally:

FLASK_APP=app/server.py FLASK_DEBUG=1 python3 -m flask run -p 5001
"""

from waitress import serve
from flask import Flask

import server_fs
import server_git

app = Flask(__name__)

app.register_blueprint(server_fs.server_fs)
app.register_blueprint(server_git.server_git)

if __name__ =='__main__':
  serve(app, host='0.0.0.0', port=5001)


