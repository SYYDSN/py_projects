from sanic_server import app
from sanic_server import port
import multiprocessing

cups = multiprocessing.cpu_count()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, workers=cups)
    pass