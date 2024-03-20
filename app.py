from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from pymongo import MongoClient
from helper_func import validate_password
import bcrypt

app = Flask(__name__)

app.secret_key = '13513ijnijdsuia7safv'

# Connect to MongoDB
client = MongoClient('mongo')
db = client['312_database']
collection = db['users']


@app.route('/', methods=['POST','GET'])
def index():
    flash_messages = dict(get_flashed_messages(with_categories=True))
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_2 = request.form['password_2']
        if password != password_2:
            flash('Password did not match', 'error')
            return redirect(url_for('register'))

        is_valid_password, password_message = validate_password(password)
        if not is_valid_password:
            flash(password_message, 'error')
            return redirect(url_for('register'))

        # Check if username already exists
        if collection.find_one({"username": username}):
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # If user does not exist, insert into database
        user_data = {
            'username': username,
            'hash_password': hashed_password,
            'salt': salt
        }

        collection.insert_one(user_data)
        flash('Registration successful!', 'success')
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
