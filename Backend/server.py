from database import init_db
from handlers import (
    ConsumptionHandler,
    LoginHandler,
    ProfileHandler,
    RegisterHandler,
)
import tornado.ioloop
import tornado.web


def make_app():
  init_db()
  return tornado.web.Application([
      (r"/api/register", RegisterHandler),
      (r"/api/login", LoginHandler),
      (r"/api/profile", ProfileHandler),
      (r"/api/consumption", ConsumptionHandler),
  ])


if __name__ == "__main__":
  app = make_app()
  app.listen(8888)
  print("🌪️ Serveur Tornado V2 actif sur http://127.0.0.1:8888")
  tornado.ioloop.IOLoop.current().start()