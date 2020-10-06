import tornado.ioloop
import tornado.web
import tornado.websocket

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

        # localhost:8888/ -> Hello, world

class IndexHandler(tornado.web.RequestHandler):
	# отображать какую-то индексную страницу
	def get(self):
		self.render("index.html")


class EchoWebSocketHandler(tornado.websocket.WebSocketHandler):
	
	def open(self):
		print('websocket is opened')

	def on_message(self, message):
		self.write_message(f" Message was sent: {message} ")

	def on_close(self):
		print('websocket is closed')



def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/index", IndexHandler),
        (r"/websocket", EchoWebSocketHandler), 
    ])


if __name__ == "__main__":
#python3 main.py or python main.py
	

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()