import socket
from Crypto.Cipher import DES  # Note: use "pycryptodome" for Python 3.6.6, not "pycrypto"
from hashlib import sha256
from time import time
from getpass import getpass
from random import SystemRandom  # Crypto secure random

def clientSocket(portToConnect):
	s = socket.socket()
	sck.settimeout(3)
	# Client always uses the 1111 port
	sck.bind(('', 1111))
	sck.connect(('', portToConnect))
	return sck

def main():
	while True:
		user = input("Type your username: ").strip('\n').encode('ascii')
		# Get key, encode ascii, hash it with sha256, get the first 8 chars of the hex of the hash and encode that
		key = sha256(getpass("Type your key: ").strip('\n').encode('ascii')).hexdigest()[:8].encode('ascii')
		cypher = DES.new(key, DES.MODE_0FB)		
		resource = input("Type which resource you want to access: ").strip('\n').encode('ascii')

		# Connect to AS
		sck = clientSocket(2222)
		msgToSend = (user + b',' + 
		             cipher.encrypt(resource + b',' + 
		                            str(int(time())).encode('ascii') + b','
		                            str(SystemRandom().randrange(10000))
		                           )
		            )
		if __debug__:
			print("Sending to AS:\n{}".format(msgToSend))
		
		sck.send(msgToSend)
		try:
			answer = sck.recv(1024)
		except socket.timeout:
			print("AS server didn't answer.\nDid you input your username and key correctly?")
			sck.close()
			continue
		
		if __debug__:
			print("AS answered:\n{}".format(answer))

		













if __name__ == "__main__":
	main()