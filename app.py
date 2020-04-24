from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/about")
def support():
    return render_template("about.html", title='About')


if __name__ == "__main__":
    app.run()
