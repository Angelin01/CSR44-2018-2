import socket
import pyDes
import threading
from random import SystemRandom
from base64 import b64encode
from base64 import b64decode

TGS_PORT = 3333

class ClientConn(threading.Thread):
	def __init__(self, conn, resources, K_tgs):
		self.conn = conn
		self.conn.settimeout(3)
		self.resources = resources
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
		# Decrypt and verify the message from the client
		# ----------------------------------------------------------------------
		# Get key from AS
		info, T_c_tgs = msg.split(b',')
		info = b64decode(info)
		T_c_tgs = b64decode(T_c_tgs)
		ID_C1, T_R1, K_c_tgs_key = self.K_tgs.decrypt(T_c_tgs).split(b',')
		K_c_tgs = pyDes.des(K_c_tgs_key, pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)

		# Get info from client
		dInfo = K_c_tgs.decrypt(info)
		if dInfo.count(b',') != 3:
			self.conn.close()
			if __debug__:
				print("Client post decrypt message format incorrect, aborting connection")
			return

		# Verify info gotten from client
		ID_C2, service, T_R2, n2 = dInfo.split(b',')
		if ID_C1 != ID_C2:
			self.conn.close()
			if __debug__:
				print("Client identification failed, aborting connection")
			return

		if T_R1 != T_R2:
			self.conn.close()
			if __debug__:
				print("Client timestamp check failed, aborting connection")
			return

		# Verify the resource
		wantedResource = None
		for resource in self.resources:
			if service == resource[0].encode('ascii'):
				wantedResource = resource

		if not wantedResource:
			self.conn.close()
			if __debug__:
				print("Requested resource doesn't exist, aborting connection")
			return

		# ----------------------------------------------------------------------
		# Craft message to send back to client
		# ----------------------------------------------------------------------
		K_s = pyDes.des(wantedResource[1][:8], pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)

		# Generate random ticket for TGS
		K_c_s = bytes(SystemRandom().getrandbits(8) for i in range(8))
		while b',' in K_c_s:
			K_c_s = bytes(SystemRandom().getrandbits(8) for i in range(8))

		T_c_s = b64encode(K_s.encrypt(b','.join([ID_C1, T_R1, K_c_s])))
		msgToReturn = b64encode(K_c_tgs.encrypt(b','.join([K_c_s, T_R1, n2]))) + b',' + T_c_s

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
		with open("tgs.csv") as file:
			entries = file.read().splitlines()
			entries = list(entry for entry in entries if entry)
	except FileNotFoundError:
		print("Could not find the 'tgs.csv' file, aborting")
		return 1

	# TGS must always be the top entry in the clients file and must start with
	# "TGS"
	tgs = entries.pop(0).strip()
	if not tgs.startswith("TGS") or tgs.count(',') != 1:
		print("'tgs.csv' format is incorrect, aborting")
		return 1
	tgs = tgs.split(',')

	# Creating the cypherer for the TGS
	K_tgs = pyDes.des(tgs[1].encode('ascii')[:8], pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)

	for entry in entries:
		if entry.count(',') != 1:
			print("'tgs.csv' format is incorrect, aborting")
			return 1

	resources = [entry.split(',') for entry in entries]

	if __debug__:
		print("Resources list:")
		print(resources)

	# --------------------------------------------------------------------------
	# Creating socket
	# --------------------------------------------------------------------------

	sck = socket.socket()
	sck.bind(('', TGS_PORT))
	sck.listen()

	while True:
		# On receiving a new connection, create a thread and return to listening
		conn, address = sck.accept()

		if __debug__:
			print("Received connection from {}".format(address))

		ClientConn(conn, resources, K_tgs).start()


if __name__ == "__main__":
	main()
