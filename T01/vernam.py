import sys
import argparse

def cypher(message, key):
	bytesMessage = bytearray(message)
	bytesKey = bytearray(key)
	output = bytearray(len(message))
	
	for i in range(len(message)):
		output[i] = bytesMessage[i] ^ bytesKey[i]
	return output

def main():
	# Parsing arguments
	parser = argparse.ArgumentParser(description='Cifrar ou decifrar mensagens com cifra de vernam.')
	parser.add_argument('-c', '--key', type=argparse.FileType('rb'), required=True, help="A chave da criptografia")
	parser.add_argument('message', nargs='?', type=argparse.FileType('rb'))
	parser.add_argument('outfile', nargs='?', type=argparse.FileType('wb'))
	args = parser.parse_args()
	
	args.outfile.write(cypher(args.message.read(), args.key.read()))
	args.outfile.close()
	
if __name__ == "__main__":
	main()