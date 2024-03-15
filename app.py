from flask import Flask, render_template, url_for, request

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():
    return render_template("index.html")

@app.route('/page1')
def page1():
    return render_template("page1.html")

@app.route('/page2')
def page2():
    return "Page 2 doesn't exist yet"

@app.route('/page3')
def page3():
    return "Page 3 doesn't exist yet"

@app.route('/page4')
def page4():
    return "Page 4 doesn't exist yet"

@app.after_request
def set_response_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
