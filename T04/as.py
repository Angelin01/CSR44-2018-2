import socket
import pyDes
import threading
from random import SystemRandom
from hashlib import sha256
from base64 import b64encode
from base64 import b64decode

AS_PORT = 2222

class ClientConn(threading.Thread):
	def __init__(self, conn, clients, K_tgs):
		self.conn = conn
		self.conn.settimeout(3)
		self.clients = clients
		self.K_tgs = K_tgs
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
				print("Client inital message format incorrect, aborting connection")
			return

		if __debug__:
			print("Received message is:\n{}".format(msg))

		# ----------------------------------------------------------------------
		# Identify the client
		# ----------------------------------------------------------------------
		ID_C, info = msg.split(b',')
		info = b64decode(info)
		ID_C = ID_C.decode('ascii')

		client = None
		for entry in self.clients:
			if entry[0] == ID_C:
				client = entry
				break

		if not client:
			self.conn.close()
			if __debug__:
				print("Client {} doesn't exist, aborting connection".format(ID_C))
			return

		# ----------------------------------------------------------------------
		# Get key from client and decode the message
		# ----------------------------------------------------------------------

		Kc = pyDes.des(client[1][:8].encode('ascii'), pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
		decryptedInfo = Kc.decrypt(info)

		if decryptedInfo.count(b',') != 2:
			self.conn.close()
			if __debug__:
				print("Client post decrypt message format incorrect, aborting connection")
			return

		service, T_R, n1 = decryptedInfo.split(b',')

		# ----------------------------------------------------------------------
		# Generate random key for TGS
		# ----------------------------------------------------------------------
		K_c_tgs = bytes(SystemRandom().getrandbits(8) for i in range(8))
		while b',' in K_c_tgs:
			K_c_tgs = bytes(SystemRandom().getrandbits(8) for i in range(8))

		# ----------------------------------------------------------------------
		# Preparing message to return to client
		# ----------------------------------------------------------------------
		T_c_tgs = b64encode(self.K_tgs.encrypt(b','.join([ID_C.encode('ascii'), T_R, K_c_tgs])))
		msgToReturn = b64encode(Kc.encrypt(b','.join([K_c_tgs, n1]))) + b',' + T_c_tgs

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

def main():
	# --------------------------------------------------------------------------
	# Reading clients list
	# --------------------------------------------------------------------------
	try:
		with open("as.csv") as file:
			entries = file.read().splitlines()
			entries = list(entry for entry in entries if entry)
	except FileNotFoundError:
		print("Could not find the 'as.csv' file, aborting")
		return 1

	# TGS must always be the top entry in the clients file and must start with
	# "TGS"
	tgs = entries.pop(0).strip()
	if not tgs.startswith("TGS") or tgs.count(',') != 1:
		print("'as.csv' format is incorrect, aborting")
		return 1
	tgs = tgs.split(',')

	# Creating the cypherer for the TGS
	K_tgs = pyDes.des(tgs[1].encode('ascii')[:8], pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)

	for entry in entries:
		if entry.count(',') != 1:
			print("'as.csv' format is incorrect, aborting")
			return 1

	clients = [entry.split(',') for entry in entries]

	if __debug__:
		print("Clients list:")
		print(clients)

	# --------------------------------------------------------------------------
	# Creating socket
	# --------------------------------------------------------------------------

	sck = socket.socket()
	sck.bind(('', AS_PORT))
	sck.listen()

	while True:
		# On receiving a new connection, create a thread and return to listening
		conn, address = sck.accept()

		if __debug__:
			print("Received connection from {}".format(address))

		ClientConn(conn, clients, K_tgs).start()


if __name__ == "__main__":
	main()
