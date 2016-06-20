import webbrowser
import threading
import SimpleHTTPServer
import SocketServer
import settings
import logging


class ServerThread(threading.Thread):

    def run(self):

        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

        self.httpd = SocketServer.TCPServer(("", 8081), Handler)
        logging.debug("serving at port 8081")

        try:
            self.httpd.serve_forever(1)
        except Exception, KeyboardInterrupt:
            logging.critical('Finishing thread exception')
        logging.debug('Finishing thread Normal')
        self.httpd.server_close()
        self.httpd.socket.close()


class OpenBrowser(threading.Thread):

	def run(self):
		url =  "http://localhost:8081/ui/webgl_loader_collada.html"
		url =  "http://localhost:8081/ui/webgl_effects_parallaxbarrier.html"
		url =  "http://localhost:8081/ui/main.html"

		webbrowser.open(url)


class Server:

    def __init__(self,address,port,connections):
        import server
        self.socket = server.WebSocket(address, port, connections, self)


if __name__ == "__main__":

    settings.init()

    logging.basicConfig(filename='example.log', filemode='w', level=eval(settings.logging))

    st = ServerThread()
    st.start()

    ob = OpenBrowser()
    ob.start()
    websocketServer = Server("127.0.0.1", 5500, 1000)
