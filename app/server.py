#!/usr/bin/env python3

"""
 To run locally:

FLASK_APP=app/server.py FLASK_DEBUG=1 python3 -m flask run -p 5001
"""

from waitress import serve
from flask import Flask
import flask_restful

import server_fs
import server_git

app = Flask(__name__)
api = flask_restful.Api(app)

api.add_resource(server_fs.FS, "/_fs/<path:path>", endpoint="fs")
api.add_resource(server_git.GIT, "/_git/<string:repo>", endpoint="git_repo")
api.add_resource(server_git.GIT, "/_git/<string:repo>/<path:path>", endpoint="git")

if __name__ =='__main__':
  serve(app, host='0.0.0.0', port=5001)


