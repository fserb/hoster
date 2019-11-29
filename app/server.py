#!/usr/bin/env python3

import re, os

from waitress import serve
from flask import Flask, send_from_directory, request, jsonify, make_response, Response, stream_with_context
import flask_restful
from flask_pymongo import MongoClient, pymongo
from flask.json import JSONEncoder
from bson.objectid import ObjectId
from bson import json_util
import magic

SERVER_PATH = os.getenv("SERVER_PATH", "www")

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
      if isinstance(obj, ObjectId):
        return str(obj)
      return json_util.default(obj)

app = Flask(__name__, static_folder=SERVER_PATH)
app.json_encoder = CustomJSONEncoder
client = MongoClient('localhost', 27017)
api = flask_restful.Api(app)

class DB(flask_restful.Resource):
  def get(self, db, collection, id=None):
    print(db, collection, id)
    if id:
      return jsonify(client[db][collection].find_one({'_id': ObjectId(id)}))
    if request.is_json:
      filter = request.get_json()
    else:
      filter = None

    limit = request.args.get('limit', default=0, type=int)

    sorts = request.args.get('sort', default="", type=str)
    sort = []

    for a in sorts.split(','):
      print(a)
      order = pymongo.ASCENDING
      if a[0] == '+':
        a = a[1:]
      elif a[0] == '-':
        order = pymongo.DESCENDING
        a = a[1:]
      sort.append((a, order))

    cursor = client[db][collection].find(filter=filter, limit=limit, sort=sort)

    return jsonify(list(cursor))

  def post(self, db, collection):
    id = client[db][collection].insert(request.get_json())
    return jsonify({"response": "OK", "id": id})

  def delete(self, db, collection, id=None):
    if id:
      client[db][collection].deleteOne({'_id': ObjectId(id)})
    else:
      client[db][collection].deleteOne(request.get_json())
    return jsonify({"response": "OK"})

  def put(self, db, collection, id):
    id = client[db][collection].updateOne({'_id', ObjectId(id)}, request.get_json())
    return jsonify({"response": "OK", "id": id})


class FS(flask_restful.Resource):
  def head(self, path):
    return self.get(path)

  def get(self, path):
    fullpath = os.path.join(SERVER_PATH, path)

    if not os.path.exists(fullpath):
      return make_response('/%s: No such file or directory.' % path, 404)

    if os.path.isdir(fullpath):
      res = make_response(jsonify(os.listdir(fullpath)))
      res.headers['Content-Type'] = 'application/json; charset=utf-8'
      return res

    mime = magic.from_file(fullpath, mime=True)
    if mime is None:
        mime = 'application/octet-stream'
    else:
        mime = mime.replace(' [ [', '')

    if request.args.get('stat') is not None:
        stat = os.stat(fullpath)
        st = {'file' : os.path.basename(fullpath),
              'path' : '/%s' % path,
              'access_time' : int(stat.st_atime),
              'modification_time' : int(stat.st_mtime),
              'change_time' : int(stat.st_ctime),
              'mimetype' : mime}
        if not os.path.isdir(fullpath):
            st['size'] = int(stat.st_size)
        res = make_response(jsonify(st))
        res.headers['Content-Type'] = 'application/json; charset=utf-8'
        return res

    stat = os.stat(fullpath)
    f = open(fullpath, "br")
    def stream_data():
        while True:
            d = f.read(8192)
            if len(d) > 0:
                yield d
            else:
                break
    res = Response(stream_with_context(stream_data()), 200, mimetype=mime, direct_passthrough=True)
    res.headers['Content-Length'] = stat.st_size
    return res

  def post(self, path):
    fullpath = os.path.join(SERVER_PATH, path)

    if os.path.exists(fullpath):
      return make_response('/%s: File exists.' % path, 403)

    data = request.get_data()

    if data == '' or data is None:
      os.mkdir(fullpath)
      return make_response('', 201)

    encoding = request.args.get('encoding', '')

    if encoding == 'base64':
        data = data.decode('base64')
    with open(fullpath, "wb") as dest_file:
        dest_file.write(data)
    return make_response('', 201)

  def delete(self, path):
    fullpath = os.path.join(SERVER_PATH, path)

    if not os.path.exists(fullpath):
      return make_response('/%s: No such file or directory.' % path, 404)

    if os.path.isdir(fullpath):
      if os.listdir(fullpath) == []:
          os.rmdir(fullpath)
          return make_response('', 204)
      else:
          return make_response('/%s: Directory is not empty.' % path, 403)

    os.remove(fullpath)
    return make_response('', 204)

api.add_resource(DB, "/db/<string:db>/<string:collection>", endpoint="collection")
api.add_resource(DB, "/db/<string:db>/<string:collection>/<string:id>", endpoint="id")
api.add_resource(FS, "/fs/<path:path>", endpoint="fs")

if __name__ =='__main__':
  serve(app, host='0.0.0.0', port=5000)


