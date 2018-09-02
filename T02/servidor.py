#!/usr/bin/python3
from hashlib import sha256
from getpass import getpass
from time import time

def registerNewUser():
	username = input("Digite o username do novo usuário: ").strip('\n')
	password = sha256(getpass("Digite a senha do novo usuário: ").strip('\n').encode('utf-8')).hexdigest()
	passwordConfirm = sha256(getpass("Digite novamente a mesma senha: ").strip('\n').encode('utf-8')).hexdigest()

	if password != passwordConfirm:
		print("*** Senhas não batem, tente novamente ***\n")
		return
		
	seedPassword = sha256((username+password).encode('utf-8')).hexdigest()
		
	with open('users', 'a') as users:
		users.write('{},{},{}\n'.format(username, password, seedPassword))
		
	print("")
	
def authenticate():
	username = input("Digite seu username: ").strip('\n')
	authInfo = None
	users = open('users', 'r').readlines()
	for user in users:
		user = user.strip('\n').split(',')
		if user[0] == username:
			authInfo = user
	if not authInfo:
		print("Usuário inválido!\n")
		return
	
	password = sha256(getpass("Digite sua senha: ").strip('\n').encode('utf-8')).hexdigest()
	if password != authInfo[1]:
		print("Senha incorreta!\n")
		return
	
	token = input("Digite seu token: ").strip('\n').upper()
	minSeedPass = authInfo[2] + str(int(time()) - int(time())%60)
	possiblePasswords = [sha256(minSeedPass.encode('utf-8')).hexdigest()]
	for i in range(1, 5):
		possiblePasswords.append(sha256(possiblePasswords[i-1].encode('utf-8')).hexdigest())
	
	for temp in possiblePasswords:
		print(temp[10:16].upper())

def main():
	while True:
		answer = input("Escolha uma opção:\n1 - Criar novo usuário\n2 - Autenticar\n").strip()
		if answer != '1' and answer != '2':
			print("Opção inválida")
			continue
		elif answer == '1':
			registerNewUser()
		elif answer == '2':
			authenticate()


if __name__ == "__main__":
	main()
