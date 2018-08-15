import sys


def cypher(message, key, chars):
	cyphered = ""
	for char in message:
		if char in chars:
			cyphered = cyphered + chars[(chars.index(char) + key) % len(chars)]
		else:
			cyphered = cyphered + char
			
	return cyphered
	
def decypher(message, key, chars):
	decyphered = ""
	for char in message:
		if char in chars:
			decyphered = decyphered + chars[(chars.index(char) - key) % len(chars)]
		else:
			decyphered = decyphered + char
			
	return decyphered
    
def main():
	characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
	
if __name__ == "__main__":
	main()
