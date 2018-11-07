import socket
import signal
from threading import Thread
from datetime import datetime


def answer404(conn):
	conn.send(("HTTP/1.1 404 Not Found\r\n" +
	           datetime.utcnow().strftime("Date: %a, %d %b %Y %H:%M:%S") + " GMT\r\n" +
	           "Server: AngelinProxy/1.0\r\n" +
	           "Content-Length: 73\r\n" +
	           "\r\n" +
	           "<html><body><h2>Erro 404</h2><h1>Página não encontrada</h1></body></html>").encode('ISO-8859-1'))


def answer400(conn):
	conn.send(("HTTP/1.1 400 Bad Request\r\n" +
	           datetime.utcnow().strftime("Date: %a, %d %b %Y %H:%M:%S") + " GMT\r\n" +
	           "Server: AngelinProxy/1.0\r\n" "Content-Type: text/html\r\n" +
	           "Content-Length: 75\r\n" +
	           "\r\n" +
	           "<html><body><h2>Erro 400</h2><h1>Requisição Mal Formada!</h1></body></html>").encode('ISO-8859-1'))


def answer403(conn):
	conn.send(("HTTP/1.1 403 Forbidden\r\n" +
	           datetime.utcnow().strftime("Date: %a, %d %b %Y %H:%M:%S") + " GMT\r\n" +
	           "Server: AngelinProxy/1.0\r\n" +
	           "Content-Type: text/html\r\n" +
	           "Content-Length: 69\r\n" +
	           "\r\n" +
	           "<html><body><h2>Erro 403</h2><h1>Acesso Bloqueado!</h1></body></html>").encode('ISO-8859-1'))

def proxy_connect(conn, addr):
	client_request = conn.recv(8192)

	if b"monitorando" in client_request:
		answer403(conn)
		conn.close()
		return

	url = client_request.split(b' ', 2)[1].split(b'/', 3)[2]

	try:
		server_ip = socket.gethostbyname(url.decode('ISO-8859-1'))
	except socket.gaierror:
		answer404(conn)
		conn.close()
		return

	print("New connection:\nClient: {}\nServer: Host: {} | IP: {}".format(addr, url.decode('ISO-8859-1'), server_ip))

	server_conn = socket.create_connection((url.decode('ISO-8859-1'), 80))
	#server_conn.settimeout(5)
	server_conn.send(client_request)
	while True:
		try:
			answer = server_conn.recv(8192)
		except socket.timeout:
			conn.send(answer)
			conn.close()
			server_conn.close()
			return

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

