import sys
import argparse

def cypher(message, key):
	return "".join([chr(a ^ b) for a,b in zip(message,key)])

def main():
	# Parsing arguments
	parser = argparse.ArgumentParser(description='Cifrar ou decifrar mensagens com cifra de vernam.')
	parser.add_argument('-c', '--key', type=argparse.FileType('rb'), required=True, help="A chave da criptografia")
	parser.add_argument('message', nargs='?', type=argparse.FileType('rb'), default=sys.stdin)
	args = parser.parse_args()
	
	print(cypher(args.message.read(), args.key.read()))
	
if __name__ == "__main__":
	main()