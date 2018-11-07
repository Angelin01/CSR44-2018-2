import socket
import signal
from proxy import AngelinProxy


def main():
	stop = False
	sck = socket.socket()

	def stop_handler(s, f):
		stop = True
		sck.close()

	signal.signal(signal.SIGTERM, stop_handler)
	signal.signal(signal.SIGINT, stop_handler)

	sck.bind(('', 8000))
	sck.listen()

	while not stop:
		conn, addr = sck.accept()
		AngelinProxy(conn, addr).start()


if __name__ == "__main__":
	main()