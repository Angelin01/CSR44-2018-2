import socket
import pyDes
from hashlib import sha256
from time import time
from getpass import getpass
from random import SystemRandom  # Crypto secure random

def main():
	socket.setdefaulttimeout(3)
	while True:
		user = input("Type your username: ").strip('\n').encode('ascii')
		# Get key, encode ascii, hash it with sha256, get the first 8 chars of the hex of the hash and encode that
		key = sha256(getpass("Type your key: ").strip('\n').encode('ascii')).hexdigest()[:8].encode('ascii')
		Kc = pyDes.des(key, pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
		resource = input("Type which resource you want to access: ").strip('\n').encode('ascii')

		# Connect to AS on port 2222
		sck = socket.create_connection(address=('localhost', 2222))
		rn1 = str(SystemRandom().randrange(10000)).encode('ascii')
		T_R = str(int(time())).encode('ascii')
		msgToSendAS = (user + b',' + 
		               Kc.encrypt(resource + b',' + 
		                          T_R + b',' +
		                          rn1))
		
		if __debug__:
			print("Sending to AS:\n{}".format(msgToSendAS))
		
		sck.send(msgToSendAS)
		try:
			answer = sck.recv(1024)
		except socket.timeout:
			print("AS server didn't answer.\nDid you input your username and key correctly?")
			sck.close()
			continue
		sck.close()

		if __debug__:
			print("AS answered:\n{}".format(answer))

		info, T_c_tgs_key = answer.split(b',')
		info = Kc.decrypt(info)

		# if the format is incorrect, abort
		if info.count(b',') != 1:
			print("Something weird happened while decrypting, aborting")
			continue
		K_c_tgs_key, n1 = info.split(b',')
		if n1 != rn1:
			print("Something weird happened while decrypting, aborting")
			continue

		# Connect to TGS on port 3333
		sck = socket.create_connection(address=('localhost', 3333))
		rn2 = str(SystemRandom().randrange(10000)).encode('ascii')
		K_c_tgs = pyDes.des(K_c_tgs_key, pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
		msgToSendTGS = (K_c_tgs.encrypt(username + b',' + resource + b',' + T_R + b',' + rn2) + b',' +
		                T_c_tgs_key)
		
		if __debug__:
			print("Sending to TGS:\n{}".format(msgToSendTGS))

		sck.send(msgToSendTGS)
		try:
			answer = sck.recv(1024)
		except socket.timeout:
			print("TGS server didn't answer.\nDid you input a valid resource?")
			sck.close()
			continue

		if __debug__:
			print("TGS answered:\n{}".format(answer))







if __name__ == "__main__":
	main()