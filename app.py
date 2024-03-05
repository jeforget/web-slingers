from flask import Flask, render_template, url_for, request

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():
    return render_template("index.html")

@app.route('/page1')
def page1():
    return "Page 1 doesn't exist yet"

@app.route('/page2')
def page2():
    return "Page 2 doesn't exist yet"

@app.route('/page3')
def page3():
    return "Page 3 doesn't exist yet"

@app.route('/page4')
def page4():
    return "Page 4 doesn't exist yet"

if __name__ == "__main__":
    app.run(debug=True)