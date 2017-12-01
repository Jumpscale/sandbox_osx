
to build a luajitenv with luarocks

```
mkdir -p /tmp/luajit
pip3 install hererocks
hererocks -j 2.1.0-beta3 -r 2.4.3 /tmp/luajit
luarocks install luafilesystem

luarocks install penlight
luarocks install lpeg
luarocks install luasystem
luarocks install luasec OPENSSL_DIR=/usr/local/opt/openssl
luarocks install redis-lua
luarocks install serpent #serialization
luarocks install inspect #visualize tables
luarocks install lua-capnproto
luarocks install lua-markdown-extra
luarocks install subprocess
luarocks install lua-cjson2
luarocks install lbase64
luarocks install luajwt --deps-mode=none OPENSSL_DIR=/usr/local/opt/openssl
#encr https://github.com/philanc/luazen
luarocks install luazen
luarocks install xxtea

##NOTWORKING
#luarocks install luatweetnacl
#luarocks install luaossl --deps-mode=none OPENSSL_DIR=/usr/local/opt/openssl

```