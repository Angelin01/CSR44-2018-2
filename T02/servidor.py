#!/usr/bin/python3

from hashlib import sha256
from getpass import getpass

def main():
	while True:
		answer = input("Escolha uma opção:\n1 - Criar novo usuário\n2 - Autenticar\n").strip()
		if answer != '1' and answer != '2':
			print("Opção inválida")
			continue
		elif answer == '1':
			username = input("Digite o username do novo usuário: ").strip('\n')
			password = sha256(getpass("Digite a senha do novo usuário: ").strip('\n').encode('utf-8')).digest()
			passwordConfirm = sha256(getpass("Digite novamente a mesma senha: ").strip('\n').encode('utf-8')).digest()

			if password != passwordConfirm:
				print("*** Senhas não batem, tente novamente *** \n")
				continue
			with open('users', 'a') as users:
				users.write('{},{}'.format(username, password))
			print("")


if __name__ == "__main__":
	main()
