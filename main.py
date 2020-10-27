import tornado.ioloop
import tornado.web
import tornado.websocket


class MessagesBuffer():

	def __init__(self, messages):

		self.__messages = []
		for m in messages:
			self.__messages.append(m)


	def add_message(self, message):
		self.__messages.append(message)


	def get_messages(self):
		return self.__messages



globalmessagebuffer = MessagesBuffer([ {"message":"The chat was started."}, {"message": "Say hello to everybody!"} ])


class IndexHandler(tornado.web.RequestHandler):
	# отображать какую-то индексную страницу
	def get(self):
		self.render("index.html", messages = globalmessagebuffer.get_messages())



class EchoWebSocketHandler(tornado.websocket.WebSocketHandler):
	
	messages = {}

	def open(self):
		print('websocket is opened')

	def on_message(self, message):
		# import time
		# key = time.strftime("%Y%m%d%H%M%S")
		new_message = {'message': message}
		
		globalmessagebuffer.add_message(new_message)

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