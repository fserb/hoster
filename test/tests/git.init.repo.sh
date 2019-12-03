$ lib/fetch GET test
[]
$ [ -d tmp/repo/test ] && echo YES
YES
$ git --git-dir tmp/repo/test/ rev-parse --is-bare-repository
true
$ git --git-dir tmp/repo/test/ branch -l -a
* master
  working
