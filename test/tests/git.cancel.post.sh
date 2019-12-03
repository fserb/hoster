$ lib/git_reset
READY

$ lib/fetch PUT test/a.txt "example file"
OK

$ lib/git_dump
refs/heads/master 1 4b825dc642cb6eb9a060e54bf8d69288fbee4904
refs/heads/working 2 497eb728207ae4220c1d5cfdbf94f5cdca39bebb
100644 blob 7897add7ea3c9519db025c1b917ac8d8df3fe17f      12        a.txt

$ lib/fetch POST test
OK

$ lib/git_dump
refs/heads/master 2 497eb728207ae4220c1d5cfdbf94f5cdca39bebb
100644 blob 7897add7ea3c9519db025c1b917ac8d8df3fe17f      12        a.txt
refs/heads/working == master

$ lib/fetch PUT test/b.txt "cancelled file"
OK

$ lib/fetch DELETE test/a.txt
OK

$ lib/git_dump
refs/heads/master 2 497eb728207ae4220c1d5cfdbf94f5cdca39bebb
100644 blob 7897add7ea3c9519db025c1b917ac8d8df3fe17f      12        a.txt
refs/heads/working 4 020cc4c0be128f73f0ba467d0e7580b9c9fdf5c7
100644 blob ea4544ea275e16ed0f29069b29364e5ef8df6bf5      14        b.txt

$ lib/fetch GET test # this should reset the working dir and undo all changes.
["a.txt"]

$ lib/git_dump
refs/heads/master 2 497eb728207ae4220c1d5cfdbf94f5cdca39bebb
100644 blob 7897add7ea3c9519db025c1b917ac8d8df3fe17f      12        a.txt
refs/heads/working == master

$ lib/fetch GET test
["a.txt"]
