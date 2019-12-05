$ lib/run "rm -rf /www/test && mkdir -p /www/test"

$ lib/fetch GET /_fs/test/
[]

$ lib/fetch POST /_fs/test/afile "this is my file"
OK

$ lib/run "echo 'simple file' > /www/test/bfile"

$ lib/fetch GET /_fs/test/afile
this is my file

$ lib/fetch GET /_fs/test/bfile
simple file

$ lib/fetch GET /_fs/test/
["afile","bfile"]

$ lib/fetch DELETE /_fs/test/afile
OK

$ lib/fetch GET /_fs/test/
["bfile"]

$ lib/fetch DELETE /_fs/test/bfile
OK

$ lib/fetch GET /_fs/test/
[]
