from pymemstore.memstore import MemStore
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from tempfile import NamedTemporaryFile
import msgpack
from datetime import datetime


class S3StoredMemStore(MemStore):

	def __init__(self, name, cred):
		super(S3StoredMemStore, self).__init__(name)
		self.cred = cred
		self.handlers["s3store"] = self.s3store
		self.handlers["s3restore"] = self.s3restore

	def get_connection(self):
		conn = S3Connection(self.cred.get("AWS_ACCESS_KEY"),self.cred.get("AWS_SECRET_KEY"))
		return conn

	def s3store(self, host, request):
		start = datetime.utcnow()
		try:
			conn = self.get_connection()
			b = conn.get_bucket(request[1])
			k = Key(b)
			k.key = request[2]
			k.content_type = "application/x-msgpack"
			fp = NamedTemporaryFile(mode="r+b")
			msgpack.pack(self.format_to_store(), fp)
			fp.seek(0)
			k.set_contents_from_file(fp)
			fp.close()
			diff = datetime.utcnow() - start
			self.socket.send(msgpack.dumps(["restored", diff.total_seconds()]))
		except Exception as e:
			import traceback
			traceback.print_exc()
			self.socket.send(msgpack.dumps(["failed", str(e)]))

	def s3restore(self, host, request):
		start = datetime.utcnow()
		try:
			conn = self.get_connection()
			conn = self.get_connection()
			b = conn.get_bucket(request[1])
			k = Key(b)
			k.key = request[2]
			fp = NamedTemporaryFile(mode="r+b")
			k.get_contents_to_file(fp)
			fp.seek(0)
			self.read_stored(msgpack.unpack(fp))
			fp.close()
			diff = datetime.utcnow() - start
			self.socket.send(msgpack.dumps(["restored", diff.total_seconds()]))
		except Exception as e:
			import traceback
			traceback.print_exc()
			self.socket.send(msgpack.dumps(["failed", str(e)]))
