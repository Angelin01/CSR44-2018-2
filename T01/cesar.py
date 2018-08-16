import sys
import argparse

def cypher(message, key, chars, decypher):
	cyphered = ""
	for char in message:
		if char in chars:
			cyphered = cyphered + chars[(chars.index(char) + (-1 if decypher else 1)*key) % len(chars)]
		else:
			cyphered = cyphered + char
			
	return cyphered
    
def main():
	# List of characters to consider on the cypher, all others are ignored
	characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
	
	# Parsing arguments
	parser = argparse.ArgumentParser(description='Cifrar ou decifrar mensagens com cifra de cesar.')
	function = parser.add_mutually_exclusive_group(required=True)
	function.add_argument('-c', '--cypher', action='store_true', help="Cifrar a mensagem")
	function.add_argument('-d', '--decypher', action='store_true', help="Decifrar a mensagem")
	parser.add_argument('-k', '--key', action='store', type=int, required=True, help="A chave da criptografia")
	parser.add_argument('file', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
	args = parser.parse_args()
	
	args.key = args.key % len(characters)
	
	print(cypher(args.file.read(), args.key, characters, False if args.cypher else True))
	
if __name__ == "__main__":
	main()
