from sanic_server import app
from sanic_server import port
import multiprocessing

cups = multiprocessing.cpu_count()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, workers=cups)
    """
    第二种工厂模式
    gunicorn sanic_server:app --bind 0.0.0.0:7011 --worker-class sanic.worker.GunicornWorker --workers 4
    """
    pass