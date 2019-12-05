$ lib/run "rm -rf /www/test && mkdir -p /www/test"

$ lib/fetch GET /_fs/test/
[]

$ lib/fetch POST /_fs/test/afile "this is my file"
OK

$ lib/fetch GET /_fs/test/afile
this is my file

$ lib/run "cat /www/test/afile"
this is my file
