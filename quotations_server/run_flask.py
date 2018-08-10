from quotations_server import socket_io, app, port


socket_io.run(app=app, port=port, host="0.0.0.0")
