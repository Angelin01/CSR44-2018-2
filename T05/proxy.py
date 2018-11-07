import socket
import signal
from threading import Thread


def answer400(conn):
	pass
	

def answer403(conn):
	pass


def proxy_connect(conn, addr):
	client_request = conn.recv(8192)
	
	url = client_request.split(b' ', 2)[1].split(b'/', 3)[2]
	
	try:
		server_ip = socket.gethostbyname(url.decode('ISO-8859-1'))
	except socket.gaierror:
		pass
		
	print("New connection:\nClient: {}\nServer: Host: {} | IP: {}".format(addr, url.decode('ISO-8859-1'), server_ip))
	
	server_conn = socket.create_connection((url.decode('ISO-8859-1'), 80))
	server_conn.settimeout(1)
	server_conn.send(client_request)
	while True:
		try:
			answer = server_conn.recv(8192)
		except socket.timeout:
			
		
		if(len(answer) > 0):
			conn.send(answer)
		else:
			break
			
	server_conn.close()
	conn.close()

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
		Thread(target=proxy_connect, args=(conn, addr)).start()


if __name__ == "__main__":
	main()

