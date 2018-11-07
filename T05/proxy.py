import socket
from threading import Thread
from datetime import datetime


class AngelinProxy(Thread):
	_basic_error_format = ("HTTP/1.1 {}\r\n" +
		                  datetime.utcnow().strftime("Date: %a, %d %b %Y %H:%M:%S") + " GMT\r\n" +
		                  "Server: AngelinProxy/1.0\r\n" +
		                  "Content-Length: {}\r\n" +
		                  "\r\n" +
		                  "{}")

	_error_values = {
		400: ("400 Bad Request", 75, "<html><body><h2>Erro 400</h2><h1>Requisição Mal Formada!</h1></body></html>"),
		403: ("403 Forbidden", 69, "<html><body><h2>Erro 403</h2><h1>Acesso Bloqueado!</h1></body></html>"),
		404: ("404 Not Found", 75, "<html><body><h2>Erro 404</h2><h1>Servidor não encontrado</h1></body></html>"),
		418: ("418 I'm a teapot", 235, "<html><body><h2>Erro 418</h2><h1>Sou um bule de chá, não um proxy</h1><p><small>Na verdade algum erro "
		                               "inesperado aconteceu e não sei o que fazer :(</small></p><p><small>Tô vazando, agora é com você! Boa "
		                               "sorte!</small></p></body></html>"),
		504: ("503 ", 74, "<html><body><h2>Erro 504</h2><h1>Servidor não respondeu</h1></body></html>")
	}

	def __init__(self, conn, addr):
		self.conn = conn
		self.addr = addr
		super().__init__()

	@staticmethod
	def _build_error(code):
		error = AngelinProxy._error_values.get(code) or AngelinProxy._error_values.get(418)
		return AngelinProxy._basic_error_format.format(error[0], error[1], error[2]).encode('ISO-8859-1')


	def run(self):
		client_request = self.conn.recv(8192)

		if b"monitorando" in client_request:
			self.conn.send(AngelinProxy._build_error(403))
			self.conn.close()
			return

		url = client_request.split(b' ', 2)[1].split(b'/', 3)[2]

		try:
			server_ip = socket.gethostbyname(url.decode('ISO-8859-1'))
		except socket.gaierror:
			self.conn.send(AngelinProxy._build_error(404))
			self.conn.close()
			return

		print("New connection:\nClient: {}\nServer: Host: {} | IP: {}".format(self.addr, url.decode('ISO-8859-1'), server_ip))

		server_conn = socket.create_connection((url.decode('ISO-8859-1'), 80))
		#server_conn.settimeout(5)
		server_conn.send(client_request)
		while True:
			try:
				answer = server_conn.recv(8192)
			except socket.timeout:
				self.conn.send(answer)
				self.conn.close()
				server_conn.close()
				return

			if(len(answer) > 0):
				self.conn.send(answer)
			else:
				break

		server_conn.close()
		self.conn.close()
