from datetime import datetime
from html import escape
from flask import Flask, redirect, render_template, url_for, request, jsonify, make_response, flash, session
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
import secrets
import hashlib
import os
from helper_func import validate_password

app = Flask(__name__)

app.secret_key = '13513ijnijdsuia7safv'

upload_folder = os.path.join('static', 'profilePics')
app.config['UPLOAD'] = upload_folder

# Connect to MongoDB
def get_db():
    client = MongoClient('mongo')
    db = client['312_database']
    # collection = db['users']
    return db


db = get_db()
collection = db['users']
posts_collection = db['posts']


@app.route('/', methods=['POST', 'GET'])
def index():
    # updated to authentication
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
        #return redirect(url_for('profile_photo'))
        if not session["profile_photo"] == None:
            filename = session["profile_photo"]
            image = os.path.join(app.config['UPLOAD'], filename)
            session['profile_photo'] = filename
            return render_template('logged_in.html', fileToUpload=image)
        return render_template("logged_in.html")
    return render_template("index.html")


@app.route('/page1')
def page1():
    return render_template("page1.html")


@app.route('/login', methods=['POST', 'GET'])
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
            session["profile_photo"] = None
            response = make_response(redirect(url_for('index')))
            response.set_cookie("Auth_token", auth_token, httponly=True, max_age=3600)
            return response

        return render_template("login.html")

    return render_template("login.html")


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session["username"] = None
    session.pop("auth", False)
    session["profile_photo"] = None
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
@app.route('/page3', methods=['GET'])
def page3():
    all_posts = list(posts_collection.find())
    return render_template("post.html", posts=all_posts )


def create_single_post(username, content):
    post = {"username": username, "content": content, "created_at": datetime.now()}
    posts_collection.insert_one(post)


# @app.route('/create_post', methods=['POST'])
# def create_post():
#     if 'username' in session:
#         content = request.form['content']
#         # Ensure to escape the content
#         content = escape(content)
#         create_single_post(session['username'], content)
#         flash('Post created successfully!', 'success')
#     return redirect(url_for('page3'))
@app.route('/create_post', methods=['POST'])
def create_post():
    if 'username' in session and (not session.get("auth", False) == False):
        content = request.form.get('content', '')
        content = escape(content)
        create_single_post(session['username'], content)
        # flash('Post created successfully!')
    return redirect(url_for('page3'))


@app.route('/like_post', methods=['POST'])
# def like_post():
# post_id = request.form.get('post_id')
# username = session.get('username')
# return jsonify({'result': 'success'})

# @app.route('/dislike_post', methods=['POST'])
# def dislike_post():
# post_id = request.form.get('post_id')
# username = session.get('username')
# return jsonify({'result': 'success'})

@app.route('/like_post', methods=['POST'])
def like_post():
    post_id = request.form.get('post_id')
    username = session.get('username')

    if not username:
        return jsonify({'result': 'error', 'message': 'Missing post ID or not logged in.'}), 400

    post_id = ObjectId(post_id)  # Convert to ObjectId for MongoDB
    post = posts_collection.find_one({"_id": post_id})

    if not post:
        return jsonify({'message': 'Post not found.'}), 404

    if username in post.get('liked', []):
        # User has already liked this post
        return jsonify({'message': 'You have already liked this post.'}), 409

    # Add the like
    if username not in post.get('liked', []):
        update_result = posts_collection.update_one(
            {"_id": post_id},
            {"$addToSet": {"liked": username}, "$inc": {"likes": 1}}
        )

    if update_result.modified_count:
        return jsonify({'result': 'success', 'total_likes': post.get('likes', 0) + 1})
    else:
        return jsonify({'message': 'Could not like the post.'}), 500


@app.route('/dislike_post', methods=['POST'])
def dislike_post():
    post_id = request.form.get('post_id')
    username = session.get('username')

    if not username:
        return jsonify({'message': 'Missing post ID or not logged in.'}), 400

    post_id = ObjectId(post_id)
    post = posts_collection.find_one({"_id": post_id})

    if not post:
        return jsonify({'message': 'Post not found.'}), 404

    if username in post.get('disliked', []):
        # User has already disliked this post
        return jsonify({'message': 'You have already disliked this post.'}), 409

    # Add the dislike
    update_result = posts_collection.update_one(
        {"_id": post_id},
        {"$addToSet": {"disliked": username}, "$inc": {"dislikes": 1}}  # $ensures no more than one per person
    )

    if update_result.modified_count:
        return jsonify({'result': 'success', 'total_dislikes': post.get('dislikes', 0) + 1})
    else:
        return jsonify({'message': 'Could not dislike the post.'}), 500

@app.route('/logged_in', methods=['POST'])
def profile_photo():
    if request.method == 'POST':
        username = session.get("username", None)
        if not username == None:
            file = request.files["fileToUpload"]
            filename = username + "profile_photo.jpg"
            file.save(os.path.join(app.config['UPLOAD'], filename))
            image = os.path.join(app.config['UPLOAD'], filename)
            session['profile_photo'] = filename
            return render_template('logged_in.html', fileToUpload=image)
        return render_template("index.html")
    return render_template("logged_in.html")



@app.after_request
def set_response_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
