$ lib/git_reset
READY

$ [ -d tmp/repo/test ] && echo $?
0

$ git --git-dir tmp/repo/test/ rev-parse --is-bare-repository
true

$ lib/git_dump
refs/heads/master 1 4b825dc642cb6eb9a060e54bf8d69288fbee4904
refs/heads/working == master
