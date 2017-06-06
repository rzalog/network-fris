class FrisServer(SocketServer.StreamRequestHandler):
	def handle(self):
		# self.rfile is a file-like object created by the handler;
		# we can now use e.g. readline() instead of raw recv() calls
		self.data = self.rfile.readline().strip()
		print "{} wrote:".format(self.client_address[0])
		print self.data
		# Likewise, self.wfile is a file-like object used to write back
		# to the client
		self.wfile.write(self.data.upper())

if __name__ == "__main__":
	HOST, PORT = "169.232.241.140", 8080

	server = SocketServer.TCPServer((HOST, PORT), FrisServer)

	server.serve_forever()