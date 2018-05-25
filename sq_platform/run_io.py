from ws_server import socket_io
from ws_server import app
from ws_server import port


if __name__ == "__main__":
    socket_io.run(app=app, host="0.0.0.0", port=port)