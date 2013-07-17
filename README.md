pymemstore
==========

We discovered a problem when writing an app that used multiple processes. We wanted to share a map of data in memory. Sharing it across processes was expensive. We tried using Pipes and Queues.  It was just trouble. We were using zeromq on some other projects and decided to give that a try.  I wrote a simple master process that holds the map in memory and responds to commands. Then I wrote a client that can talk to it, getting and setting key/values pairs. I also added a set feature that you can have a set of values and ensure their are no duplicates.  It worked great.  Far easier to setup and ues than the alternatives. 

After a bit I realized it needed a way to restore and save it's current state to an from a file. So I added that functionality. Then I thought, wouldn't it be nice to have that state be a file on S3.  Boom done.

This is just a start.  It's a bit crude.  It uses message pack for data storage and message passing. zeromq for communication.

future
======

Features I'd like to add in the future.
* security/authentication - I haven't tested this but I think that other processes could tap into this.
* Right now it is tied to using IPC sockets, want to make it support TCP sockets as well.
* distributed map - sharding? or just replication to and from other instances.
