"""
Very simple memory store.

I could add limits and expirations to make it work more like memcached, but I won't... for now.
I do want to add the ability to have multiple servers serve the same tables, but that is just a dream.
"""

from pymemstore.core import Feeder, BackChannel, ShutdownException
import resource
import msgpack
from datetime import datetime


class MemStore(BackChannel):

	def __init__(self, name):
		super(MemStore, self).__init__(name)
		self.store = {}
		self.sets = {}

	def table(self, name):
		if name not in self.store.keys():
			self.store[name] = {}
		return self.store[name]

	def set_named(self, name):
		if name not in self.sets.keys():
			self.sets[name] = set()
		return self.sets[name]

	def handle_request(self, data):
		request = msgpack.loads(data)
		op = request[0]
		if op == "all":
			table = request[1]
			if table in self.store.keys():
				self.socket.send(msgpack.dumps(self.store[table]))
			else:
				self.socket.send(msgpack.dumps(-1))
		elif op == "info":
			mb_used = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0
			self.socket.send(msgpack.dumps([mb_used, "mb"]))
		elif op == "store":
			start = datetime.utcnow()
			try:
				fp = open(request[1], 'w')
				with fp:
					msgpack.pack(self._format_to_store(), fp)
				diff = datetime.utcnow() - start
				self.socket.send(msgpack.dumps(["stored", diff.total_seconds()]))
			except Exception as e:
				self.socket.send(msgpack.dumps(["failed", str(e)]))
		elif op == "restore":
			start = datetime.utcnow()
			try:
				fp = open(request[1], 'r')
				with fp:
					self._read_stored(msgpack.unpack(fp))
				diff = datetime.utcnow() - start
				self.socket.send(msgpack.dumps(["restored", diff.total_seconds()]))
			except Exception as e:
				self.socket.send(msgpack.dumps(["failed", str(e)]))
		elif op == "done":
			self.socket.send(msgpack.dumps(["ok"]))
			raise ShutdownException()
		elif op == "set":
			table = request[1]
			key = request[2]
			val = request[3]
			self.table(table)[key] = val
			self.socket.send(msgpack.dumps(1))
		elif op == "get":
			table = request[1]
			key = request[2]
			self.socket.send(msgpack.dumps(self.table(table).get(key)))
		elif op == "push":
			table = request[1]
			key = request[2]
			self.set_named(table).add(key)
			self.socket.send(msgpack.dumps(1))
		elif op == "pull":
			table = request[1]
			key = request[2]
			self.set_named(table).remove(key)
			self.socket.send(msgpack.dumps(1))
		elif op == "in_set":
			table = request[1]
			key = request[2]
			self.socket.send(msgpack.dumps(key in self.set_named(table)))
		elif op == "list_set":
			table = request[1]
			self.socket.send(msgpack.dumps(list(self.set_named(table))))
		elif op == "clear_set":
			table = request[1]
			self.set_named(table).clear()
			self.socket.send(msgpack.dumps(1))
		else:
			self.socket.send(msgpack.dumps(-1))

	def _read_stored(self, data):
		if data.get("version", 0) == 1:
			self.store = data.get("store")
			self.sets = data.get("sets")
		else:
			raise Exception("incompatable data file, only version 1 is supported")

	def _format_to_store(self):

		return {
			"version": 1,
			"store": self.store,
			"sets": {key: list(value) for key, value in self.sets.iteritems()},
		}


class MemStoreClient(Feeder):
	started = False

	def handle_response(self, data):
		try:
			rsp = msgpack.loads(data)
			if rsp == 1:
				self.response = True
			elif rsp < 0:
				self.response = False
			else:
				self.response = rsp
		except msgpack.exceptions.ExtraData:
			# this is generally a byproduct of shutdown.
			return False

	def start(self):
		super(MemStoreClient, self).start()
		self.started = True

	def stop(self):
		super(MemStoreClient, self).stop()
		self.started = False

	def put(self, table, key, value):
		if not self.started:
			self.start()
		self.response = None
		self.send_message(msgpack.dumps(["set", table, key, value]))
		return self.response

	def get(self, table, key):
		if not self.started:
			self.start()
		self.response = None
		self.send_message(msgpack.dumps(["get", table, key]))
		return self.response

	def info(self):
		if not self.started:
			self.start()
		self.response = None
		self.send_message(msgpack.dumps(["info"]))
		return self.response

	def done(self):
		if not self.started:
			self.start()
		self.response = None
		self.send_message(msgpack.dumps(["done"]))
		return self.response

	def all(self, table):
		if not self.started:
			self.start()
		self.response = None
		self.send_message(msgpack.dumps(["all", table]))
		return self.response

	def store(self, filename):
		if not self.started:
			self.start()
		self.response = None
		self.send_message(msgpack.dumps(["store", filename]), timeout=15000)
		return self.response

	def restore(self, filename):
		if not self.started:
			self.start()
		self.response = None
		self.send_message(msgpack.dumps(["restore", filename]), timeout=15000)
		return self.response

	def push(self, set_name, value):
		"""
		pushes a value onto a set
		"""
		if not self.started:
			self.start()
		self.response = None
		self.send_message(msgpack.dumps(["push", set_name, value]))
		return self.response

	def pull(self, set_name, value):
		"""
		pulls(removes) a value from a set
		"""
		if not self.started:
			self.start()
		self.response = None
		self.send_message(msgpack.dumps(["pull", set_name, value]))
		return self.response

	def in_set(self, set_name, value):
		"""
		returns true if a value is in a set otherwise false
		"""
		if not self.started:
			self.start()
		self.response = None
		self.send_message(msgpack.dumps(["in_set", set_name, value]))
		return self.response

	def list_set(self, set_name):
		"""
		returns all values in the named set
		"""
		if not self.started:
			self.start()
		self.response = None
		self.send_message(msgpack.dumps(["list_set", set_name]))
		return self.response

	def clear_set(self, set_name):
		"""
		returns all values in the named set
		"""
		if not self.started:
			self.start()
		self.response = None
		self.send_message(msgpack.dumps(["clear_set", set_name]))
		return self.response

