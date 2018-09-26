import socket
import threading
import pyDes
from time import time
from hashlib import sha256
from getpass import getpass
from base64 import b64encode
from base64 import b64decode


class ClientConn(threading.Thread):
	def __init__(self, conn, id, K_s):
		self.conn = conn
		self.conn.settimeout(3)
		self.id = id
		self.K_s = K_s
		super().__init__()

	def run(self):
		# ----------------------------------------------------------------------
		# Get message from client
		# ----------------------------------------------------------------------
		try:
			msg = self.conn.recv(1024)
		except socket.timeout:
			self.conn.close()
			if __debug__:
				print("Client didn't send anything, aborting connection")
			return

		# If format is incorrect, just ignore
		if msg.count(b',') != 1:
			self.conn.close()
			if __debug__:
				print("Client initial message format incorrect, aborting connection")
			return

		if __debug__:
			print("\nReceived message is:\n{}".format(msg))

		# ----------------------------------------------------------------------
		# Parse received info
		# ----------------------------------------------------------------------
		info, T_c_s = msg.split(b',')
		info = b64decode(info)
		T_c_s = b64decode(T_c_s)

		T_c_s_info = self.K_s.decrypt(T_c_s)
		# If format is incorrect, just ignore
		if T_c_s_info.count(b',') != 2:
			self.conn.close()
			if __debug__:
				print("Client T_c_s message format incorrect, aborting connection")
			return

		ID_C1, T_R1, K_c_s_key = T_c_s_info.split(b',')
		K_c_s = pyDes.des(K_c_s_key, pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
		dInfo = K_c_s.decrypt(info)

		if dInfo.count(b',') != 3:
			self.conn.close()
			if __debug__:
				print("Client message format incorrect, aborting connection")
			return

		# ----------------------------------------------------------------------
		# Verify received info
		# ----------------------------------------------------------------------
		ID_C2, T_R2, S_R, n3 = dInfo.split(b',')

		if ID_C1 != ID_C2:
			self.conn.close()
			if __debug__:
				print("Client id doesn't match, aborting connection")
			return

		if T_R1 != T_R2:
			self.conn.close()
			if __debug__:
				print("Timestamp doesn't match, aborting connection")
			return
			
		# Verify that time is ok
		if int(time() - int(T_R1.decode('ascii')) ) > 60:
			self.conn.close()
			if __debug__:
				print("Client ticket expired, aborting connection")
			return

		if self.id != S_R:
			self.conn.close()
			if __debug__:
				print("Service ID provided doesn't match mine, aborting connection")
			return

		# ----------------------------------------------------------------------
		# Craft message to return to client
		# ----------------------------------------------------------------------
		msgToReturn = b64encode(K_c_s.encrypt(b','.join([b"OK", n3])))

		if __debug__:
			print("Answering to client:\n{}".format(msgToReturn))

		# ----------------------------------------------------------------------
		# Sending message to client
		# ----------------------------------------------------------------------
		try:
			self.conn.send(msgToReturn)
		except BrokenPipeError:
			pass
		self.conn.close()
		return

def main(id):
	K_s = pyDes.des(sha256(getpass("Type my token: ").encode('ascii')).hexdigest()[:8].encode('ascii'),
	                pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)

	sck = socket.socket()
	sck.bind(('', int(id)))
	sck.listen()

	while True:
		try:
			# On receiving a new connection, create a thread and return to listening
			conn, address = sck.accept()

			if __debug__:
				print("Received connection from {}".format(address))

			ClientConn(conn, id.encode('ascii'), K_s).start()
		except KeyboardInterrupt:
			sck.close()
			print("\n")
			break


if __name__ == "__main__":
	id = input("Input my id (used as a port): ")
	main(id)
