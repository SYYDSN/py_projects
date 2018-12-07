from flask import Flask,request,render_template
import os
import json

app = Flask(__name__)

data_dir_path = os.path.split(__file__)[0]


@app.route("/cc", methods=['post'])
def process_driving_data():
    if request.method.lower() == "post" and len(request.files) > 0:
        name_list = list()
        for k, v in request.files.items():
            file = request.files[k]
            file_name = file.filename.lower()
            data_path = os.path.join(data_dir_path, file_name)
            file.save(data_path)
            name_list.append(file_name)
        return json.dumps(name_list)


@app.route("/upload")
def xx():
    return render_template("upload.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True, threaded=True)
