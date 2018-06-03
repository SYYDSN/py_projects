from flask import Flask
from flask import send_file
from flask import make_response
from flask import render_template
import mongo_db
from io import BytesIO


app = Flask(__name__)


@app.route('/<file_name>')
def hello_world(file_name):
    r = mongo_db.BaseFile.find_one_cls(collection="case_file",
                                       filter_dict={"file_name": "2018-05-28 18-42-07屏幕截图.png"})
    resp = make_response(send_file(BytesIO(r['data']), attachment_filename="1.png", as_attachment=True))
    # resp = make_response(send_file("static/image/{}".format(file_name), as_attachment=True))
    return resp


@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
