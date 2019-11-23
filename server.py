#!/usr/bin/env python3

import re, os

from waitress import serve
from flask import Flask, send_from_directory, request, jsonify
import flask_restful
from flask_pymongo import MongoClient, pymongo
from flask.json import JSONEncoder
from bson.objectid import ObjectId
from bson import json_util

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
      if isinstance(obj, ObjectId):
        return str(obj)
      return json_util.default(obj)

app = Flask(__name__, static_folder=os.getenv("SERVER_PATH", "www"))
app.json_encoder = CustomJSONEncoder
client = MongoClient('localhost', 27017)
api = flask_restful.Api(app)

class Everything(flask_restful.Resource):
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


api.add_resource(Everything, "/db/<string:db>/<string:collection>", endpoint="collection")
api.add_resource(Everything, "/db/<string:db>/<string:collection>/<string:id>", endpoint="id")

@app.route('/')
def index():
  return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def send(path):
  return send_from_directory(app.static_folder, path)

if __name__ =='__main__':
  serve(app, host='0.0.0.0', port=5000)


