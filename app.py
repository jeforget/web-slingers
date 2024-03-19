from flask import Flask, redirect, render_template, url_for, request, jsonify, make_response, flash, session
from pymongo import MongoClient
import bcrypt
import secrets
import hashlib



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
@app.route('/', methods=['POST','GET'])
def index():
    auth = request.cookies.get("Auth_token", None)
    if not auth == None:
        auth = auth.encode()
        hashed_token_user = hashlib.md5(auth).hexdigest()
        my_data = collection.find_one({"Auth_token": hashed_token_user}, {"_id": False})
        if my_data == None:
            return render_template("index.html")

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
            flash("Username does not exist")
            return redirect(url_for('index'))

        password = password.encode()

        salt = my_data["salt"]
        salted_password = bcrypt.hashpw(password, salt)
        if bcrypt.checkpw(password, my_data["hash_password"]):
            auth_token = secrets.token_hex(16)
            hashed_token = hashlib.md5(auth_token.encode()).hexdigest()
            collection.update_one({"username": username}, {"$set": {"Auth_token": hashed_token}})

            response = make_response(render_template("index.html"))
            response.set_cookie("Auth_token", auth_token, httponly=True)
            flash("Logged in successfully")
            session["username"] = username
            return response
        return render_template("login.html", info="Invalid username or password")

    return render_template("login.html")

@app.route('/logout', methods=['POST','GET'])
def logout():
    response = make_response(render_template("index.html"))
    response.delete_cookie("Auth_token")
    session.pop("username")

    return response

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
