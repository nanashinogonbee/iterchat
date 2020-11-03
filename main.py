import tornado.ioloop
import tornado.web
import tornado.websocket


def singleton(cls):
	instances = {}

	import functools

	@functools.wraps(cls)
	def get_instance(*args, **kwargs):
		if cls not in instances:
			instances[cls] = cls(*args, **kwargs)
		return instances[cls]
	return get_instance


@singleton
class MessagesBuffer():

	def __init__(self):
		from collections import deque
		self.__messages = deque(maxlen=50)


	def add_message(self, message):
		self.__messages.append(message)


	def get_messages(self):
		return self.__messages



globalmessagebuffer = MessagesBuffer()

globalmessagebuffer.add_message({"id": "0", "message":"The chat was started."}) 
globalmessagebuffer.add_message({"id": "0", "message": "Say hello to everybody!"})

# globalmessagebuffer или MessageBuffer() -> обращаемся к одному и тому же объекту.


class IndexHandler(tornado.web.RequestHandler):
	# отображать какую-то индексную страницу
	def get(self):
		self.render("index.html", messages = globalmessagebuffer.get_messages())



class EchoWebSocketHandler(tornado.websocket.WebSocketHandler):
	
	messages = {}

	def open(self):
		print('websocket is opened')

	def on_message(self, message):

		import uuid

		id = uuid.uuid4()

		# import time
		# key = time.strftime("%Y%m%d%H%M%S")
		new_message = {'id': id.hex,  'message': message}
		
		globalmessagebuffer.add_message(new_message)
		print(f"{ new_message.get('id', 'Unknown ID') } write {new_message.get('message', 'Empty message')}")
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