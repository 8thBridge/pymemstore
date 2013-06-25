import zmq
from multiprocessing import Process
import msgpack


class ShutdownException(Exception):
	pass


class BackChannel(Process):
	"""
	A fun little class that can take requests from multiple feeders and aggregate the responses
	"""
	def __init__(self, name):
		super(BackChannel, self).__init__()
		self.name = name

	def run(self):
		self.listening = True
		self.context = zmq.Context()
		# pylint: disable=E1101
		self.socket = self.context.socket(zmq.REP)
		self.socket.bind("ipc://{0}".format(self.name))
		try:
			while self.listening:
				request = self.socket.recv()
				self.handle_request(request)
		except ShutdownException:
			print "got message to shutdown"
			self.stop_listening()

	def stop_listening(self):
		self.listening = False
		self.socket.close()
		self.context.term()

	def handle_request(self, data):
		self.socket.send("ok")


class Feeder(object):
	"""
	Feeder class that feeds data into the backchannel.
	"""
	TIMEOUT = 1000

	def __init__(self, name):
		self.name = name
		self.context = zmq.Context()
		# pylint: disable=E1101
		self.socket = self.context.socket(zmq.REQ)
		self.socket.setsockopt(zmq.LINGER, 0)
		self.poll = zmq.Poller()
		self.poll.register(self.socket, zmq.POLLIN)

	def start(self):
		self.socket.connect("ipc://{0}".format(self.name))

	def stop(self):
		self.socket.close()
		self.context.term()

	def send_message(self, message, timeout=None):
		if not timeout:
			timeout = self.TIMEOUT
		self.socket.send(message)
		socks = dict(self.poll.poll(timeout))
		# pylint: disable=E1101
		if socks.get(self.socket) == zmq.POLLIN:
			response = self.socket.recv()
		else:
			response = msgpack.packb({"error": "timeout", "message": "send timeout"})
		self.handle_response(response)

	def handle_response(self, data):
		pass
