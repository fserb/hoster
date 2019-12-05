import os
import functools

import pygit2
from flask import Blueprint, send_from_directory, request, jsonify, \
  make_response, Response, stream_with_context
import magic

"""
_git:

GET repo/ - returns a list of files and subfiles of the repo, resets any commit
GET repo/<path> - returns the content of the file
PUT repo/<path> - replace file without commit
DELETE repo/<path> - delete file without commit
POST repo/ - commit repo

"""

SERVER_REPO_PATH = os.getenv("SERVER_REPO_PATH", "repo")

server_git = Blueprint('server_git', __name__)

def git_auto_insert(git, treebuilder, path, thing, mode):
  path_parts = path.split('/', 1)
  if len(path_parts) == 1:
    treebuilder.insert(path, thing, mode)
    return treebuilder.write()

  subtree_name, sub_path = path_parts
  subtree = treebuilder.get(subtree_name)
  if subtree:
    sub_builder = git.TreeBuilder(subtree.id)
  else:
    sub_builder = git.TreeBuilder()

  subtree = git_auto_insert(git, sub_builder, sub_path, thing, mode)

  treebuilder.insert(subtree_name, subtree, pygit2.GIT_FILEMODE_TREE)
  return treebuilder.write()

def git_auto_delete(git, treebuilder, path):
  path_parts = path.split('/', 1)
  if len(path_parts) == 1:
    if not treebuilder.get(path):
      return None
    treebuilder.remove(path)
    return treebuilder.write()

  subtree_name, sub_path = path_parts
  subtree = treebuilder.get(subtree_name)
  if not subtree:
    return
  sub_builder = git.TreeBuilder(subtree.id)

  subtree = git_auto_delete(git, sub_builder, sub_path)

  treebuilder.insert(subtree_name, subtree, pygit2.GIT_FILEMODE_TREE)
  return treebuilder.write()


def git_auto_get(git, tree, path):
  path_parts = path.split('/', 1)
  if len(path_parts) == 1:
    return tree[path]

  subtree_name, sub_path = path_parts
  subtree = tree[subtree_name]
  if not subtree:
    return None
  return git_auto_get(git, git[subtree.id], sub_path)


def git_auto_list(git, tree, path, out):
  for e in tree:
    if e.type == "blob":
      out.append(path + e.name)
    elif e.type == "tree":
      git_auto_list(git, git[e.id], path + e.name + "/", out)


@server_git.route('/_git/<string:repo>', methods=['HEAD', 'GET'])
def get_repo(repo):
  repo = os.path.join(SERVER_REPO_PATH, repo)

  if not os.path.isdir(repo):
    pygit2.init_repository(repo, bare=True)
    git = pygit2.Repository(repo)
    tree = git.TreeBuilder().write()
    commit = git.create_commit('refs/heads/master',
      pygit2.Signature("GET " + request.full_path, request.remote_addr + "@hoster"),
      pygit2.Signature("hoster", "@hoster"),
      'repo init', tree, [])
    git.branches.local.create("working", git[commit])

  git = pygit2.Repository(repo)
  head = git.lookup_reference("refs/heads/master").target
  commit = git[head]

  if 'working' in git.branches:
    if git.branches['working'].target != head:
      git.branches['working'].delete()
  if not 'working' in git.branches:
    git.branches.local.create("working", commit)

  out = []
  git_auto_list(git, commit.tree, "", out)

  res = make_response(jsonify(out))
  res.headers['Content-Type'] = 'application/json; charset=utf-8'
  return res


@server_git.route('/_git/<string:repo>/<path:path>', methods=['HEAD', 'GET'])
def get_path(repo, path):
  repo = os.path.join(SERVER_REPO_PATH, repo)

  if not os.path.isdir(repo):
    return make_response('/%s: Unknown repo.' % repo, 404)

  git = pygit2.Repository(repo)
  head = git.lookup_reference("refs/heads/master").target
  commit = git[head]

  try:
    entry = git_auto_get(git, commit.tree, path)
    blob = git[entry.id]
  except KeyError:
    return make_response('/%s: file does not exist.' % path, 404)

  mime = magic.from_buffer(blob.data)
  if mime is None:
      mime = 'application/octet-stream'
  else:
      mime = mime.replace(' [ [', '')
  res = make_response(blob.data)
  res.headers['Content-Type'] = mime
  return res

@server_git.route('/_git/<string:repo>/<path:path>', methods=['PUT'])
def put_path(repo, path):
  repo = os.path.join(SERVER_REPO_PATH, repo)
  if not os.path.isdir(repo):
    return make_response('/%s: Unknown repo.' % repo, 404)

  git = pygit2.Repository(repo)
  head = git.lookup_reference("refs/heads/working").target
  commit = git[head]

  data = request.get_data()
  encoding = request.args.get('encoding', '')
  if encoding == 'base64':
      data = data.decode('base64')

  id = git.create_blob(data)
  blob = git[id]

  tb = git.TreeBuilder(commit.tree)
  tree = git_auto_insert(git, tb, path, id, pygit2.GIT_FILEMODE_BLOB)
  wt = git.lookup_reference("refs/heads/working").target

  git.create_commit('refs/heads/working',
    pygit2.Signature("PUT " + request.full_path, request.remote_addr + "@hoster"),
    pygit2.Signature("hoster", "@hoster"),
    '', tree, [wt])

  return make_response("OK")


@server_git.route('/_git/<string:repo>', methods=['POST'])
def post_repo(repo):
  repo = os.path.join(SERVER_REPO_PATH, repo)
  if not os.path.isdir(repo):
    return make_response('/%s: Unknown repo.' % repo, 404)

  git = pygit2.Repository(repo)
  headw = git.lookup_reference("refs/heads/working").target
  commitw = git[headw]

  head = git.lookup_reference("refs/heads/master").target

  if commitw.tree != git[head].tree:
    commit = git.create_commit('refs/heads/master',
      pygit2.Signature("POST " + request.full_path, request.remote_addr + "@hoster"),
      pygit2.Signature("hoster", "@hoster"),
      '', commitw.tree.id, [head])

  if git.branches['working'].target != head:
    head = git.lookup_reference("refs/heads/master").target
    git.branches['working'].delete()
    git.branches.local.create("working", git[head])

  return make_response("OK")


@server_git.route('/_git/<string:repo>/<path:path>', methods=['DELETE'])
def delete(repo, path):
  repo = os.path.join(SERVER_REPO_PATH, repo)

  git = pygit2.Repository(repo)
  head = git.lookup_reference("refs/heads/working").target
  commit = git[head]

  tb = git.TreeBuilder(commit.tree)
  tree = git_auto_delete(git, tb, path)
  if not tree:
    return make_response('/%s: file not found.' % path, 404)

  wt = git.lookup_reference("refs/heads/working").target

  git.create_commit('refs/heads/working',
    pygit2.Signature("DELETE " + request.full_path, request.remote_addr + "@hoster"),
    pygit2.Signature("hoster", "@hoster"),
    '', tree, [wt])

  return make_response("OK")


