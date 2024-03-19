from flask import Flask, redirect, render_template, url_for, request, jsonify, make_response
from pymongo import MongoClient
import bcrypt
import secrets
import hashlib
app = Flask(__name__)

mongo_client = MongoClient("mongodb://cse312:27017/")
db = mongo_client["users_database"]
users_collection = db["users"]

@app.route('/', methods=['POST','GET'])
def index():
    return render_template("index.html")

@app.route('/page1')
def page1():
    return render_template("page1.html")

@app.route('/page2', methods=['POST','GET'])
def page2():
    if request.method == 'POST':

        username = request.form['username_login']
        password = request.form['password_login']
        my_data = users_collection.find_one({'username': username}, {"_id": False})
        if my_data is None:
            return render_template("login.html", info="Invalid username or password")
        password = password.encode()

        salt = my_data["salt"]
        salted_password = bcrypt.hashpw(password, salt)
        if bcrypt.checkpw(password, my_data["hash_password"]):
            auth_token = secrets.token_hex(16)
            hashed_token = hashlib.md5(auth_token.encode()).hexdigest()

            users_collection.update_one({"username": username}, {"$set": {"Auth_token": hashed_token}})
            response = make_response(redirect(url_for('index')))
            response.set_cookie("Auth_token", auth_token, httponly=True)
            return response
        return render_template("login.html", info="Invalid username or password")

    return render_template("login.html")



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
