$ lib/run "rm -rf /www/test && mkdir -p /www/test"

$ lib/fetch GET /_fs/test/
[]

$ lib/fetch POST /_fs/test/dir/afile "this is my file"
OK

$ lib/fetch POST /_fs/test/dir/afile "update"
OK

$ lib/fetch GET /_fs/test/dir/afile
update

$ lib/run "cat /www/test/dir/afile"
update

$ lib/fetch GET /_fs/test/
["dir/afile"]
