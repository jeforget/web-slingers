from flask import Flask, redirect, render_template, url_for, request, jsonify, make_response, flash, session, datetime
from pymongo import MongoClient
import bcrypt
import secrets
import hashlib
from helper_func import validate_password

app = Flask(__name__)

app.secret_key = '13513ijnijdsuia7safv'

# Connect to MongoDB
def get_db():
    client = MongoClient('mongo')
    db = client['312_database']
    #collection = db['users']
    return db

db = get_db()
collection = db['users']
posts_collection = db['posts']

def create_post(username, content):
    post = {"username": username, "content": content, "created_at": datetime.now()}
    posts_collection.insert_one(post)

@app.route('/', methods=['POST','GET'])
def index():
    #updated to authentication
    auth = request.cookies.get("Auth_token", None)
    if not auth == None:
        auth = auth.encode()
        hashed_token_user = hashlib.md5(auth).hexdigest()
        my_data = collection.find_one({"Auth_token": hashed_token_user}, {"_id": False})

        if my_data == None:
            session.pop("auth", False)
            return render_template("index.html")
        if session["username"] == None:
            session.pop("auth", False)
            return render_template("index.html")
        if not my_data.get("username") == session["username"]:
            session["auth"] = False
            response = make_response(render_template("index.html"))
            response.set_cookie("Auth_token", "zero", httponly=True)
            return response
        return render_template("logged_in.html")
    return render_template("index.html")

@app.route('/page1')
def page1():
    return render_template("page1.html")

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username_login']
        password = request.form['password_login']

        my_data = collection.find_one({'username': username}, {"_id": False})
        # User is not registered
        if my_data is None:
            return redirect(url_for('index'))

        password = password.encode()
        salt = my_data["salt"]

        if bcrypt.checkpw(password, my_data["hash_password"]):

            auth_token = secrets.token_hex(16)
            hashed_token = hashlib.md5(auth_token.encode()).hexdigest()
            collection.update_one({"username": username}, {"$set": {"Auth_token": hashed_token}})
            session["username"] = username
            session["auth"] = True
            response = make_response(redirect(url_for('index')))
            response.set_cookie("Auth_token", auth_token, httponly=True)

            return response

        return render_template("login.html")

    return render_template("login.html")

@app.route('/logout', methods=['POST','GET'])
def logout():
    session["username"] = None
    session.pop("auth", False)
    response = make_response(redirect(url_for("index")))
    response.delete_cookie("Auth_token")
    return response

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
# post page
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
