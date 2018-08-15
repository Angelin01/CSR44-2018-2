import sys
import argparse


def decypher(message, key, chars):
	decyphered = ""
	for char in message:
		if char in chars:
			decyphered = decyphered + chars[(chars.index(char) - key) % len(chars)]
		else:
			decyphered = decyphered + char
			
	return decyphered

def analyseFrequency(message, chars):
	# Three highest frequencies are "a", "e" and "o", try those
	counts = [0] * len(chars)
	for char in message:
		if char in chars:
			counts[chars.index(char)] = counts[chars.index(char)] + 1
		
	mostFrequent = counts.index(max(counts))
	print("Três mensagens mais provaveis:\n")
	for char in ['a', 'e', 'o']:
		key = (mostFrequent - chars.index(char)) % len(chars)
		print(decypher(message, key, chars) + '\n')

def main():
	# List of characters to consider on the cypher, all others are ignored
	characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
	
	# Parsing arguments
	parser = argparse.ArgumentParser(description='Cifrar ou decifrar mensagens com cifra de cesar.')
	parser.add_argument('file', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
	args = parser.parse_args()
	
	analyseFrequency(args.file.read(), characters)
	
if __name__ == "__main__":
	main()