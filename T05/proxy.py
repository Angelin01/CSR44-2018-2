import socket
import signal
from threading import Thread


def main():
	stop = False
	sck = socket.socket()
	
	def stop_handler(s, f):
		stop = True
		sck.close()
		
	signal.signal(signal.SIGTERM, stop_handler)
	signal.signal(signal.SIGTINT, stop_handler)
	
	sck.bind(('', 8000))
	sck.listen()
	while True:
		conn, addr = sck.accept()
		Thread(target=proxy_connect, args=(conn,)).start()

if __name__ == "__main__":
	main()

