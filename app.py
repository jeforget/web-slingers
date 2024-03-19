from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
app = Flask(__name__)

app.secret_key = '13513ijnijdsuia7safv'

# Connect to MongoDB
client = MongoClient('mongo')
db = client['312_database']
collection = db['users']


@app.route('/', methods=['POST','GET'])
def index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        if collection.find_one({'email': email}) or collection.find_one({"username": username}):
            flash('Email or username already exists!')
            return redirect(url_for('index'))

        # If user does not exist, insert into database
        user_data = {
            'username': username,
            'email': email,
            'password': password
        }
        collection.insert_one(user_data)
        flash('Registration successful!')
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/page1')
def page1():
    return render_template("page1.html")


@app.route('/page2')
def page2():
    return "Page 2 doesn't exist yet"


@app.after_request
def set_response_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
