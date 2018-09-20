import socket
import pyDes
import threading
from random import SystemRandom
from hashlib import sha256

TGS_PORT = 3333

class ClientConn(threading.Thread):
	def __init__(self, conn, resources, K_tgs):
		self.conn = conn
		self.conn.settimeout(3)
		self.resources = resources
		self.K_tgs = K_tgs
		super().__init__()

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
		print("Clients list:")
		print(clients)

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
