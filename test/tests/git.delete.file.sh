$ lib/git_reset
READY

$ lib/fetch PUT test/a.txt "example file"
OK

$ lib/fetch PUT test/b.txt "another file"
OK

$ lib/git_dump
refs/heads/master 1 4b825dc642cb6eb9a060e54bf8d69288fbee4904
refs/heads/working 3 cb4541c127c3abcc1ef4ae71e9d086a73f8c6c3a
100644 blob 7897add7ea3c9519db025c1b917ac8d8df3fe17f      12        a.txt
100644 blob cdcb28483da7783a8b505a074c50632a5481a69b      12        b.txt

$ lib/fetch GET test/b.txt # files should not be available before commit.
/b.txt: file does not exist.
HTTP code: 404

$ lib/fetch DELETE test/b.txt
OK

$ lib/fetch DELETE test/b.txt
/b.txt: file not found.
HTTP code: 404

$ lib/git_dump
refs/heads/master 1 4b825dc642cb6eb9a060e54bf8d69288fbee4904
refs/heads/working 4 497eb728207ae4220c1d5cfdbf94f5cdca39bebb
100644 blob 7897add7ea3c9519db025c1b917ac8d8df3fe17f      12        a.txt

$ lib/fetch POST test
OK

$ lib/git_dump
refs/heads/master 2 497eb728207ae4220c1d5cfdbf94f5cdca39bebb
100644 blob 7897add7ea3c9519db025c1b917ac8d8df3fe17f      12        a.txt
refs/heads/working == master

$ lib/fetch GET test
["a.txt"]

$ lib/fetch GET test/a.txt
example file
