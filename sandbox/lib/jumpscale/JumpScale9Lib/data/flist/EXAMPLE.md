## Installation
Make sure you have the required dependencies
```python
j.tools.prefab.local.development.rocksdb.install()
j.tools.prefab.local.development.g8storeclient.install()
```

## Creating a plist
```python
kvs = j.data.kvs.getRocksDBStore('flist', namespace=None, dbpath='/tmp/demo-flist.db')
f = j.tools.flist.getFlist(rootpath='/tmp/', kvs=kvs)
f.add('/tmp/')                                                                           
f.upload("ardb.server", 16379)
```
