from meinheld import server
from Message_Server import app, port

# meinheld 方式,部分c的py.
server.listen(("0.0.0.0", port))
print("message server running by meinheld on {} port....".format(port))
server.run(app)
