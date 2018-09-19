import socket
import pyDes
import threading
from random import SystemRandom
from hashlib import sha256

class ClientConn(threading.Thread):
	def __init__(self, conn, clients, K_tgs):
		self.conn = conn
		self.conn.settimeout(3)
		self.clients = clients
		self.K_tgs = K_tgs
		super().__init__()

	def run(self):
		try:
			msg = self.conn.recv(1024)
		except socket.timeout:
			self.conn.close()
			if __debug__:
				print("Client didn't send anything, aborting connection")
			return

		if msg.count(b',') != 1:
			self.conn.close()
			if __debug__:
				print("Client inital message format incorrect, aborting connection")
			return

		if __debug__:
			print("Received message is:\n{}".format(msg))

		ID_C, info = msg.split(b',')
		ID_C = ID_C.decode('ascii')

		client = None
		for entry in self.clients:
			if entry[0] == ID_C:
				client = entry
				break
		
		if not client:
			if __debug__:
				self.conn.close()
				print("Client {} doesn't exist, aborting connection".format(ID_C))
				return

		Kc = pyDes.des(client[1][:8].encode('ascii'), pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
		decryptedInfo = Kc.decrypt(info)

		if decryptedInfo.count(b',') != 2:
			conn.close()
			if __debug__:
				print("Client post decrypt message format incorrect, aborting connection")
			return
		
		service, T_R, n1 = decryptedInfo.split(b',')
		K_c_tgs = bytes(SystemRandom().getrandbits(8) for i in range(8))
		print(K_c_tgs)
		T_c_tgs = self.K_tgs.encrypt(b','.join([ID_C.encode('ascii'), T_R, K_c_tgs]))
		msgToReturn = Kc.encrypt(b','.join([K_c_tgs, n1])) + b',' + T_c_tgs

		if __debug__:
			print("Answering to client:\n{}".format(msgToReturn))

		self.conn.send(msgToReturn)
		self.conn.close()
		return


def main():
	try:
		with open("as.csv") as file:
			entries = file.read().splitlines()
			entries = list(entry for entry in entries if entry)
	except FileNotFoundError:
		print("Could not find the 'as.csv' file, aborting")
		return 1
	
	tgs = entries.pop(0).strip()
	if not tgs.startswith("TGS") or tgs.count(',') != 1:
		print("'as.csv' format is incorrect, aborting")
		return 1
	tgs = tgs.split(',')
	K_tgs = pyDes.des(tgs[1].encode('ascii')[:8], pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)

	for entry in entries:
		if entry.count(',') != 1:
			print(entry)
			print(entry.count(','))
			print("'as.csv' format is incorrect, aborting")
			return 1
	
	clients = [entry.split(',') for entry in entries]

	if __debug__:
		print("Clients list:")
		print(clients)
	
	sck = socket.socket()
	sck.bind(('', 2222))
	sck.listen()

	while True:
		conn, address = sck.accept()

		if __debug__:
			print("Received connection from {}".format(address))

		ClientConn(conn, clients, K_tgs).start()


if __name__ == "__main__":
	main()