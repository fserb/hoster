import os

from flask import Blueprint, send_from_directory, request, jsonify, \
  make_response, Response, stream_with_context
import magic

SERVER_PATH = os.getenv("SERVER_PATH", "www")

server_fs = Blueprint('server_fs', __name__)

@server_fs.route('/_fs/<path:path>', methods=['HEAD', 'GET'])
def get(path):
  fullpath = os.path.join(SERVER_PATH, path)

  if not os.path.exists(fullpath):
    return make_response('/%s: No such file or directory.' % path, 404)

  if os.path.isdir(fullpath):
    all = []
    for d, ns, fs in os.walk(fullpath):
      dp = os.path.relpath(d, fullpath)
      if dp == '.': dp = ''
      for f in fs:
        all.append(os.path.join(dp, f))
    res = make_response(jsonify(sorted(all)))
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


@server_fs.route('/_fs/<path:path>', methods=['POST'])
def post(path):
  fullpath = os.path.join(SERVER_PATH, path)

  data = request.get_data()
  encoding = request.args.get('encoding', '')
  if encoding == 'base64':
      data = data.decode('base64')

  dir = os.path.dirname(fullpath)
  os.makedirs(dir, exist_ok=True)

  with open(fullpath, "wb") as dest_file:
      dest_file.write(data)

  return make_response("OK")


@server_fs.route('/_fs/<path:path>', methods=['DELETE'])
def delete(path):
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
  return make_response("OK")
