$ lib/git_reset
READY

$ lib/fetch PUT test/a.txt "example file"
OK

$ lib/fetch POST test
OK

$ lib/git_dump
refs/heads/master 2 497eb728207ae4220c1d5cfdbf94f5cdca39bebb
100644 blob 7897add7ea3c9519db025c1b917ac8d8df3fe17f      12        a.txt
refs/heads/working == master

$ docker exec -it hoster.test /usr/bin/git --git-dir /repo/test branch -q -d working

$ lib/git_dump
refs/heads/master 2 497eb728207ae4220c1d5cfdbf94f5cdca39bebb
100644 blob 7897add7ea3c9519db025c1b917ac8d8df3fe17f      12        a.txt

$ lib/fetch GET test
["a.txt"]
