import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object("server-config")

@app.route("/upload", methods=["POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        _file = request.files["file"]
        if _file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if _file:
            filename = secure_filename(_file.filename)
            _file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return "OK"


@app.route("/", methods=["GET"])
def index():
    return """
    <!DOCTYPE html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method="post" enctype="multipart/form-data" action="/upload">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    """
