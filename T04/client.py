import socket
import pyDes
from hashlib import sha256
from time import time
from getpass import getpass
from random import SystemRandom  # Crypto secure random

AS_PORT = 2222
TGS_PORT = 3333

def main():
	socket.setdefaulttimeout(3)
	while True:
		# ----------------------------------------------------------------------
		# Gathering user input
		# ----------------------------------------------------------------------

		user = input("Type your username: ").strip('\n').encode('ascii')
		# Get key, encode ascii, hash it with sha256, get the first 8 chars of the hex of the hash and encode that
		key = sha256(getpass("Type your key: ").strip('\n').encode('ascii')).hexdigest()[:8].encode('ascii')
		Kc = pyDes.des(key, pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
		resource = input("Type which resource you want to access: ").strip('\n').encode('ascii')

		# ----------------------------------------------------------------------
		# Prepare message to send AS
		# ----------------------------------------------------------------------

		# Connect to AS on port 2222
		try:
			sck = socket.create_connection(address=('localhost', AS_PORT))
		except socket.timeout:
			print("AS appears to be down. Try again later.")
			continue

		rn1 = str(SystemRandom().randrange(10000)).encode('ascii')
		T_R = str(int(time())).encode('ascii')
		msgToSendAS = user + b',' + Kc.encrypt(b','.join([resource, T_R, rn1]))

		if __debug__:
			print("Sending to AS:\n{}".format(msgToSendAS))

		# ----------------------------------------------------------------------
		# Talking to AS
		# ----------------------------------------------------------------------

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

		infoAS, T_c_tgs = answer.split(b',')
		info = Kc.decrypt(infoAS)

		# if the format is incorrect, abort
		if info.count(b',') != 1:
			print("Something weird happened while decrypting, aborting")
			continue
		K_c_tgs_key, n1 = info.split(b',')
		if n1 != rn1:
			print("Something weird happened while decrypting, aborting")
			continue

		# ----------------------------------------------------------------------
		# Prepare message to send TGS
		# ----------------------------------------------------------------------

		# Connect to TGS on port 3333
		try:
			sck = socket.create_connection(address=('localhost', TGS_PORT))
		except socket.timeout:
			print("TGS appears to be down. Try again later.")
			continue

		rn2 = str(SystemRandom().randrange(10000)).encode('ascii')
		K_c_tgs = pyDes.des(K_c_tgs_key, pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
		msgToSendTGS = K_c_tgs.encrypt(b','.join([username, resource, T_R, rn2])) + b',' + T_c_tgs

		if __debug__:
			print("Sending to TGS:\n{}".format(msgToSendTGS))

		# ----------------------------------------------------------------------
		# Talking to TGS
		# ----------------------------------------------------------------------

		sck.send(msgToSendTGS)
		try:
			answer = sck.recv(1024)
		except socket.timeout:
			print("TGS server didn't answer.\nDid you input a valid resource?")
			sck.close()
			continue

		if __debug__:
			print("TGS answered:\n{}".format(answer))

		infoTGS, T_c_s = answer.split(b',')
		info = K_c_tgs.decrypt(infoTGS)

		# if the format is incorrect, abort
		if info.count(b',') != 2:
			print("Something weird happened while decrypting, aborting")
			continue
		K_c_s_key, T_A, n2 = info.split(b',')
		if rn2 != n2:
			print("Something weird happened while decrypting, aborting")
			continue

		# ----------------------------------------------------------------------
		# Prepare message to send resource
		# ----------------------------------------------------------------------

		# Connect to resource on it's port (same as resource id)
		try:
			sck = socket.create_connection(address=('localhost', int(resource)))
		except socket.timeout:
			print("TGS appears to be down. Try again later.")
			continue

		rn3 = str(SystemRandom().randrange(10000)).encode('ascii')
		K_c_s = pyDes.des(K_c_s_key, pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
		msgToSendService = K_c_s.encrypt(b','.join([username, T_A, resource, rn3])) + b',' + T_c_s

		if __debug__:
			print("Sending to Service:\n{}".format(msgToSendService))

		# ----------------------------------------------------------------------
		# Talking to resource
		# ----------------------------------------------------------------------

		sck.send(msgToSendService)
		try:
			answer = sck.recv(1024)
		except socket.timeout:
			print("Service didn't answer.\nAre you trying something fishy?")
			sck.close()
			continue

		infoService = K_c_s.decrypt(answer)
		if infoService.count(b',') != 1:
			print("Something weird happened while decrypting, aborting")
			continue
		answerService, n3 = infoService.split(b',')

		if n3 != rn3:
			print("Something weird happened while decrypting, aborting")
			continue

		# ----------------------------------------------------------------------
		# Finishing
		# ----------------------------------------------------------------------

		if answerService == b"OK":
			print("* ============ *\n*** SUCCESS! ***\n* ============ *")
			continue
		else:
			print("Authentication failure! Service did not recognize you!")

if __name__ == "__main__":
	main()
