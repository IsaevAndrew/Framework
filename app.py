import json
from datetime import datetime

from server import SimpleFramework
from response import HtmlResponse, Response, JsonResponse, TextResponse

app = SimpleFramework()


@app.route("/")
def index(app):
    return HtmlResponse(app.render_template("index.html", {
        "title": "WFW",
        "message": "Welcome to the Web Framework!"
    }))


@app.route("/time")
def time(app):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return HtmlResponse(app.render_template("time.html", {
        "title": "Current Time",
        "time": current_time
    }))


@app.route("/submit", methods=["GET", "POST"])
def submit(app):
    data = {"name": "Иван Иванов", "email": "ivan@example.com",
            "message": "Привет, мир!"}
    return HtmlResponse(app.render_template("submit.html", {
        "title": "Данные отправлены",
        "data": json.dumps(data, ensure_ascii=False, indent=4)
    }))


@app.route('/user/<username>')
def show_user(username):
    return TextResponse(f"Hello {username} !")


@app.route('/user/<username>/json', methods=["GET"])
def show_user(app, username):
    return JsonResponse({"username": username})


if __name__ == "__main__":
    app.start_server()
