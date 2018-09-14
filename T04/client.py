import socket
import pyDes
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
		Kc = pyDes.des(key, pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)		
		resource = input("Type which resource you want to access: ").strip('\n').encode('ascii')

		# Connect to AS on port 2222
		sck = clientSocket(2222)
		rn1 = str(SystemRandom().randrange(10000)).encode('ascii')
		msgToSend = (user + b',' + 
		             Kc.encrypt(resource + b',' + 
		                        str(int(time())).encode('ascii') + b',' +
		                        rn1
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
		sck.close()

		if __debug__:
			print("AS answered:\n{}".format(answer))

		info, T_c_tgs = answer.split(b',')
		info = Kc.decrypt(info)

		# if the format is incorrect, abort
		if info.count(b',') != 1:
			print("Something weird happened while decrypting, aborting")
			continue
		K_c_tgs, n1 = info.split(b',')
		if n1 != rn1:
			print("Something weird happened while decrypting, aborting")
			continue
		#
		#sck = clientSocket(3333)












if __name__ == "__main__":
	main()