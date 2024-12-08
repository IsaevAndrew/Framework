from datetime import datetime

from server import SimpleFramework
from response import HtmlResponse, Response

app = SimpleFramework()


@app.route("/")
def index(app):
    return HtmlResponse(app.render_template("index.html", {
        "title": "Home",
        "message": "Welcome to the Web Framework!"
    }))


@app.route("/time")
def time(app):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return HtmlResponse(app.render_template("time.html", {
        "title": "Current Time",
        "time": current_time
    }))

@app.route('/user/<username>')
def show_user(username):
    return Response(f"Hello {username} !")

if __name__ == "__main__":
    app.start_server()
