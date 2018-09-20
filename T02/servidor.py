#!/usr/bin/python3
from hashlib import sha256
from getpass import getpass
from time import time
import string
import random
import os

def registerNewUser():
	# Gerar sal aleatorio de tamanho 4
	saltSeed = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(4)).encode('utf-8')
	saltMain = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(4)).encode('utf-8')

	username = input("Digite o username do novo usuário: ").strip('\n')
	password = sha256(getpass("Digite a senha local do novo usuário: ").strip('\n').encode('utf-8') + saltMain).hexdigest()
	passwordConfirm = sha256(getpass("Digite novamente a mesma senha: ").strip('\n').encode('utf-8') + saltMain).hexdigest()

	if password != passwordConfirm:
		print("*** Senhas não batem, tente novamente ***\n")
		return
		
	seedPassword = sha256(getpass("Digite a senha semente: ").strip('\n').encode('utf-8') + saltSeed).hexdigest()
	seedPasswordConfirm = sha256(getpass("Digite novamente a senha semente: ").strip('\n').encode('utf-8') + saltSeed).hexdigest()

	if seedPassword != seedPasswordConfirm:
		print("*** Senhas semente não batem, tente novamente ***\n")
		return

	with open('users', 'a') as users:
		users.write('{},{},{},{},{}\n'.format(username, password, seedPassword, saltMain.decode('utf-8'), saltSeed.decode('utf-8')))
		
	print("")
	
def authenticate():
	# Autenticação normal
	username = input("Digite seu username: ").strip('\n')
	authInfo = None

	with open('users', 'a+'):   # Criar arquivo de autenticacao se nao existe
		pass

	users = open('users', 'r').readlines()
	for user in users:
		user = user.strip('\n').split(',')
		if user[0] == username:
			authInfo = user
	if not authInfo:
		print("Usuário inválido!\n")
		return

	# Ler tokens invalidos para esse usuario
	with open('invalidTokens', 'a+'):  # Criar arquivo de invalidos se nao existe
		pass

	invalidatedTokens = []
	with open('invalidTokens', 'r') as invalidFile:
		for line in invalidFile.readlines():
			line = line.strip('\n').split(',')
			if line[0] == authInfo[0]:
				invalidatedTokens.append(line[1])
	
	token = input("Digite seu token: ").strip('\n').upper()
	# Checa o tempo só depois que o usuario digita o token por facilidade
	minSeedPass = authInfo[2] + str(int(time()) - int(time())%60)

	# Gera o primeiro token
	possibleTokens = [sha256(minSeedPass.encode('utf-8')).hexdigest()]
	if possibleTokens[0] in invalidatedTokens:  # Checa se o token não é invalido
		print("Token inválido!\n")
		return
	if token == possibleTokens[0][10:16].upper():  # Checa se o token é o digitado
		print("Autenticação realizada com sucesso!\n")
		with open('invalidTokens', 'a') as invalidTokens:
			invalidTokens.write("{},{}\n".format(authInfo[0], possibleTokens[0]))
		return

	# Gera os demais tokens, 1 de cada vez, verifica se não é inválido e se é o digitado
	for i in range(1, 5):
		possibleTokens.append(sha256(possibleTokens[i-1].encode('utf-8')).hexdigest())
		if possibleTokens[i] in invalidatedTokens:
			print("Token inválido!\n")
			return
		if token == possibleTokens[i][10:16].upper():
			print("Autenticação realizada com sucesso!\n")
			with open('invalidTokens', 'a') as invalidTokens:
				invalidTokens.write("{},{}\n".format(authInfo[0], possibleTokens[i]))
			return
	print("Token inválido!\n")

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
