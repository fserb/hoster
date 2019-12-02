import os
import functools

import pygit2
from flask import send_from_directory, request, jsonify, make_response, Response, stream_with_context
import flask_restful
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


class GIT(flask_restful.Resource):
  def head(self, repo, path):
    return self.get(path)

  def get(self, repo, path=None):
    repo = os.path.join(SERVER_REPO_PATH, repo)

    if not path: # full repo info
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
      git.reset(head, pygit2.GIT_RESET_SOFT)

      commit = git[head]
      out = []
      git_auto_list(git, commit.tree, "", out)
      print(sorted(out))
      res = make_response(jsonify(out))
      res.headers['Content-Type'] = 'application/json; charset=utf-8'
      return res

    if not os.path.isdir(repo):
      return make_response('/%s: Unknown repo.' % repo, 404)

    git = pygit2.Repository(repo)
    head = git.lookup_reference("refs/heads/working").target
    commit = git[head]

    entry = git_auto_get(git, commit.tree, path)
    blob = git[entry.id]

    mime = magic.from_buffer(blob.data)
    if mime is None:
        mime = 'application/octet-stream'
    else:
        mime = mime.replace(' [ [', '')
    res = make_response(blob.data)
    res.headers['Content-Type'] = mime
    return res


  def put(self, repo, path):
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


  def post(self, repo, path=None):
    if path:
      return make_response('Invalid POST with path', 404)

    repo = os.path.join(SERVER_REPO_PATH, repo)
    if not os.path.isdir(repo):
      return make_response('/%s: Unknown repo.' % repo, 404)

    git = pygit2.Repository(repo)
    headw = git.lookup_reference("refs/heads/working").target
    commitw = git[headw]

    head = git.lookup_reference("refs/heads/master").target

    commit = git.create_commit('refs/heads/master',
      pygit2.Signature("POST " + request.full_path, request.remote_addr + "@hoster"),
      pygit2.Signature("hoster", "@hoster"),
      '', commitw.tree.id, [head])

    git.branches['working'].set_target(commit)


  def delete(self, repo, path):
    repo = os.path.join(SERVER_REPO_PATH, repo)

    git = pygit2.Repository(repo)
    head = git.lookup_reference("refs/heads/working").target
    commit = git[head]

    tb = git.TreeBuilder(commit.tree)
    tree = git_auto_delete(git, tb, path)
    wt = git.lookup_reference("refs/heads/working").target

    git.create_commit('refs/heads/working',
      pygit2.Signature("DELETE " + request.full_path, request.remote_addr + "@hoster"),
      pygit2.Signature("hoster", "@hoster"),
      '', tree, [wt])

