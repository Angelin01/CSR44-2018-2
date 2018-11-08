import socket
from threading import Thread
from datetime import datetime


class AngelinProxy(Thread):
	_basic_error_format = ("HTTP/1.1 {}\r\n" +
	                       "Date: {} GMT\r\n" +
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
		self.client_headers = {}
		self.client_request = None
		self.server_headers = {}
		self.server_response = None
		super().__init__()

	@staticmethod
	def _build_error(code):
		print("BUILDING ERROR CODE", code)
		error = AngelinProxy._error_values.get(code) or AngelinProxy._error_values.get(418)
		return AngelinProxy._basic_error_format.format(error[0], datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S"), error[1], error[2]).encode('ISO-8859-1')

	def parse_headers(self, message, is_client):
		fields = message.decode('ISO-8859-1').split('\r\n\r\n')[0].split('\r\n')
		output = self.client_headers if is_client else self.server_headers
		output["Request"] = fields[0]
		fields = fields[1:]
		for field in fields:
			key, value = field.split(':', 1)
			output[key] = value

		if is_client and not "Host" in output:
			raise ValueError("Malfored Request")

	def run(self):
		try:
			self.client_request = self.conn.recv(8192)

			# ---------------------------------------------- #
			# Check for "monitorando" to display access blocked
			if b"monitorando" in self.client_request:
				self.conn.send(AngelinProxy._build_error(403))
				self.conn.close()
				return
			# ---------------------------------------------- #

			# ---------------------------------------------- #
			# Find and connect to requested host
			try:
				self.parse_headers(self.client_request, True)
			except Exception:  # Malformed request
				self.conn.send(AngelinProxy._build_error(400))
				self.conn.close()
				return

			self.client_headers["Host"] = self.client_headers["Host"].strip()
			if ':' in self.client_headers["Host"]:
				url, port = self.client_headers["Host"].rsplit(':', 1)
				port = int(port)
			else:
				url = self.client_headers["Host"]
				port = 443 if "https" in self.client_headers["Request"] else 80

			try:
				server_ip = socket.gethostbyname(url)
				server_conn = socket.create_connection((url, port), timeout=1)
			except socket.timeout:
				self.conn.send(AngelinProxy._build_error(504))
				self.conn.close()
				return
			except socket.gaierror:
				self.conn.send(AngelinProxy._build_error(404))
				self.conn.close()
				return

			print("New connection:\nClient: {}\nServer: Host: {} | IP: {}".format(self.addr, url, server_ip))
			# ---------------------------------------------- #
			# Talk with server
			try:
				server_conn.send(self.client_request)
			except socket.timeout:
				self.conn.send(AngelinProxy._build_error(504))
				self.conn.close()
				return

			# Keep looping until we find the end of the headers
			data = b""
			while b"\r\n\r\n" not in data:
				try:
					data += server_conn.recv(128)
				except socket.timeout:
					pass

				# Received empty data, connection is done
				if not data:
					break

			if not data:
				server_conn.close()
				self.conn.close()
				return

			headers, extra = data.split(b"\r\n\r\n", 1)
			self.parse_headers(headers, False)

			try:
				if "Content-Length" in self.server_headers:
					data += server_conn.recv(int(self.server_headers["Content-Length"]) - len(extra))
					self.conn.sendall(data)
				else:
					while True:
						buffer = server_conn.recv(4096)
						if not buffer:
							break
						self.conn.sendall(buffer)

			except socket.timeout:
				pass

			server_conn.close()
			self.conn.close()
			return

		except Exception as e:
			# Oh no, something weird happened
			print("Error, stopping")
			print("Args:", e.args)
			print(e)

			if self.client_request:
				self.conn.send(AngelinProxy._build_error(418))
				self.conn.close()

			return
