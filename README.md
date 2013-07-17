pymemstore
==========

We discovered a problem when writing an app that used multiple processes. We wanted to share a map of data in memory. Sharing it across processes was expensive. We tried using Pipes and Queues.  It was just trouble. We were using zeromq on some other projects and decided to give that a try.  I wrote a simple master process that holds the map in memory and responds to commands. Then I wrote a client that can talk to it, getting and setting key/values pairs. I also added a set feature that you can have a set of values and ensure their are no duplicates.  It worked great.  Far easier to setup and ues than the alternatives. 

After a bit I realized it needed a way to restore and save it's current state to an from a file. So I added that functionality. Then I thought, wouldn't it be nice to have that state be a file on S3.  Boom done.

This is just a start.  It's a bit crude.  It uses message pack for data storage and message passing. zeromq for communication.

future
======

Features I'd like to add in the future.
- [ ] security/authentication - I haven't tested this but I think that other processes could tap into this.
- [ ] Right now it is tied to using IPC sockets, want to make it support TCP sockets as well.
- [ ] distributed map - sharding? or just replication to and from other instances.


How to use it
=============

To run the master process.
```python
from pymemstore import MemStore
memstore = MemStore("memstore")
memstore.start()  # starts listening on the ipc socket.
```

To start with the S3 store support enabled do this instead.
(I do want to make this just be part of a settings files instead doing it this way)
```python
from pymemstore.s3store import S3StoredMemStore
memstore = S3StoredMemStore(
    "memstore",
    {
      "AWS_ACCESS_KEY": AWS_ACCESS_KEY,
      "AWS_SECRET_KEY": AWS_SECRET_KEY
    })
memstore.start()  # starts listening on the ipc socket.
```
Create a Client:
```python
client = MemStoreClient("memstore")
client.start()
```

Sending commands:
```python
client.send(["<command>", "arg1"..."argN"])
```

Commands
========

### store
store the current state to a file
```python
>> client.send(["store", "<file location to store state to>"])
["stored", <time in seconds it took>]
```

### restore
restore the current state from a file
```python
>> client.send(["store", "<file location to restore state from>"])
["restored", <time in seconds it took>]
```

### info
Determines the amount of memory being used by the service.
```python
>> client.send(["info"])
[<mb_used>, "mb"]
```

### all
Returns the map of all the data stored. Only really useful for small datasets.
```python
>> client.send(["all", "<table name>"])
{....}
```

### set
Sets a key's value, does not need to be a string, can be any basic datatype.
```python
>> client.send(["set", "<table name>", "<key>", <value>])
1
```

### get
Gets a key's value.
```python
>> client.send(["get", "<table name>", "<key>"])
<value>
```

### done
Shutdown the service
```python
>> client.send(["done"])
["ok"]
```

### push
Pushes a value onto a set. Value must be a hashable type, like a string.
```python
>> client.send(["push", "<set name>", value])
1
```

### pull
Pulls a value off of a set. Value must be a hashable type, like a string.
```python
>> client.send(["pull", "<set name>", value])
1
```

### in_set
Pulls a value off of a set. Value must be a hashable type, like a string.
```python
>> client.send(["in_set", "<set name>", value])
True # or False
```

### list_set
Returns all values in the named set.
```python
>> client.send(["list_set", "<set name>"])
[...]
```

### clear_set
Clears all values in the named set.
```python
>> client.send(["clear_set", "<set name>"])
1
```



