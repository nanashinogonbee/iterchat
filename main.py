import tornado.ioloop
import tornado.web
import tornado.websocket


class IndexHandler(tornado.web.RequestHandler):
	# отображать какую-то индексную страницу
	def get(self):
		self.render("index.html")


class EchoWebSocketHandler(tornado.websocket.WebSocketHandler):
	
	messages = {}

	def open(self):
		print('websocket is opened')

	def on_message(self, message):

		import time
		key = time.strftime("%Y%m%d%H%M%S")
		EchoWebSocketHandler.messages[key] = message
		print(EchoWebSocketHandler.messages)
		self.write_message(f" Message was sent: {message} ")

	def on_close(self):
		print('websocket is closed')



def make_app():
    return tornado.web.Application([
        (r"/", IndexHandler),
        (r"/websocket", EchoWebSocketHandler),
    ], debug = True)


if __name__ == "__main__":
#python3 main.py or python main.py
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()