$ lib/git_reset
READY

$ lib/fetch PUT test/a.txt "example file"
null

$ lib/git_dump
master != working
refs/heads/master 4b825dc642cb6eb9a060e54bf8d69288fbee4904
refs/heads/working 497eb728207ae4220c1d5cfdbf94f5cdca39bebb
100644 blob 7897add7ea3c9519db025c1b917ac8d8df3fe17f      12  a.txt

$ lib/fetch POST test
null

$ lib/git_dump
master == working
refs/heads/master 497eb728207ae4220c1d5cfdbf94f5cdca39bebb
100644 blob 7897add7ea3c9519db025c1b917ac8d8df3fe17f      12  a.txt
refs/heads/working 497eb728207ae4220c1d5cfdbf94f5cdca39bebb
100644 blob 7897add7ea3c9519db025c1b917ac8d8df3fe17f      12  a.txt

$ lib/fetch GET test/a.txt
example file

