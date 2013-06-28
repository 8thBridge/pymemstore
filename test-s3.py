if __name__ == "__main__":
	"""
	Simple tests.  TODO - write up real unit tests and make this thing sing
	"""
	import resource
	import msgpack
	from pymemstore import MemStoreClient
	from pymemstore.s3store import S3StoredMemStore

	AWS_ACCESS_KEY = "< put your key here >"
	AWS_SECRET_KEY = "< put your key here >"

	store = S3StoredMemStore("main", {"AWS_ACCESS_KEY": AWS_ACCESS_KEY, "AWS_SECRET_KEY": AWS_SECRET_KEY})
	store.start()

	client = MemStoreClient("main")

	print client.info()
	print client.send(["s3restore", "< put your bucket here >", "test-data.msgpack"])
	print client.info()

	for x in range(20):
		client.put("table_one", "{0:06d}".format(x), "test value {0}")

	print client.info()

	for x in range(10):
		client.put("table_two", "{0:04d}".format(x), "best value {0}".format(x))

	print "store", client.info()
	print "client", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0, "mb"
	print client.send(["s3store", "< put your bucket here >", "test-data.msgpack"])
	print client.get("table_two", "0045")
	full_table = client.all("table_two")
	print "{0} records found".format(len(full_table.keys()))
	print "store", client.info()
	print "client", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0, "mb"

	print "=" * 80
	print "push tests"
	print "=" * 80
	print "push", client.push("test-set", "0045"), "0045"
	print "push", client.push("test-set", "1045"), "1045"
	print "pull", client.pull("test-set", "1045"), "1045"
	print "in_set", client.in_set("test-set", "0045"), "0045"
	print "in_set", client.in_set("test-set", "1045"), "1045"

	print client.send(["s3store", "< put your bucket here >", "test-data.msgpack"])

	client.send_message(msgpack.dumps(["done"]))
	client.stop()
	print "client", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0, "mb"
