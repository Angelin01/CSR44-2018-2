#!/usr/bin/python3
from hashlib import sha256
from time import time
from getpass import getpass

def main():
	while True:
		username = input("\nDigite seu usuário: ")
		seed = None

		with open('users', 'a+'):
			pass
		with open('users') as users:
			for user in users.readlines():
				user = user.strip('\n').split(',')
				if user[0] == username:
					seedSalt = user[4]

		if not seedSalt:
			print("Usuário não existe!")
			continue
		seed = sha256(getpass("Digite sua senha seed: ").strip('\n').encode('utf-8') + seedSalt.encode('utf-8')).hexdigest()

		print("Os tokens para este minuto são:")
		minSeedPass = seed + str(int(time()) - int(time()) % 60)
		tokens = [sha256(minSeedPass.encode('utf-8')).hexdigest()]
		print(tokens[0][10:16].upper())
		for i in range(1,5):
			tokens.append(sha256(tokens[i-1].encode('utf-8')).hexdigest())
			print(tokens[i][10:16].upper())

if __name__ == "__main__":
	main()
