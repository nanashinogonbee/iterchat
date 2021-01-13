import asyncio
import collections

import tornado.ioloop
import tornado.locks
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
        self.cond = tornado.locks.Condition()
        self.__messages = collections.deque(maxlen=50)


    def add_message(self, message):
        self.__messages.append(message)

        self.cond.notify_all()


    def get_messages(self):
        return self.__messages

    def get_messages_since(self, cursor):
        results = []

        for msg in reversed(self.__messages):
            if msg['id'] == cursor:
                break
            results.append(msg)
        results.reverse()
        return results


globalmessagebuffer = MessagesBuffer()


class IndexHandler(tornado.web.RequestHandler):
    # отображать какую-то индексную страницу
    def get(self):
        self.render("index.html", messages=globalmessagebuffer.get_messages())



class EchoWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print('websocket is opened')


    def on_message(self, message):
        import uuid
        id = uuid.uuid4()
        new_message = {
            'id': str(id),
            'from_id': uuid.getnode(),
            'nick': message.split(': ', 1)[0],
            'message': message.split(': ', 1)[1]
            }
        
        globalmessagebuffer.add_message(new_message)

        print(f"Message #{ new_message.get('id', 'Unknown ID') } {new_message.get('message', 'Empty message')}")
        self.write_message(f"{new_message}")

    def on_close(self):
        print('websocket is closed')


class MessageUpdatesHandler(tornado.web.RequestHandler):
    """docstring for MessageUpdatesHandler"""
    async def post(self):
        cursor = self.get_argument("cursor", None)
        messages = globalmessagebuffer.get_messages_since(cursor)

        while not messages:
            self.wait_future = globalmessagebuffer.cond.wait()
            try:
                await self.wait_future
            except asyncio.CancelledError:
                return 

            messages = globalmessagebuffer.get_messages_since(cursor)

        if self.request.connection.stream.closed():
            return

        print(f"cursor {cursor} ")
        print(messages)
        self.write(dict(messages=messages))

    def on_connection_close(self):
        self.wait_future.cancel()


class StatsHandler(tornado.web.RequestHandler):
    def get(self):
        messages = globalmessagebuffer.get_messages()
        stats = {}
        for msg in messages:
            stats.update({msg['nick']: 0})
        for msg in messages:
            stats[msg['nick']] += 1
        stats = [{'nick': k, 'qty': v} for k, v in stats.items()]
        self.render("stats.html", stats=stats)


def make_app():
    return tornado.web.Application([
        (r"/", IndexHandler),
        (r"/websocket", EchoWebSocketHandler),
        (r"/message/update", MessageUpdatesHandler),
        (r"/stat", StatsHandler),
    ], debug = True)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
