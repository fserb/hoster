$ lib/run "rm -rf /www/test && mkdir -p /www/test"

$ lib/run "echo 'simple file' > /www/test/afile"

$ lib/fetch GET /_fs/test/
["afile"]

$ lib/fetch GET /_fs/test/afile
simple file

