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
from flask_socketio import SocketIO, emit
import threading

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
        # return redirect(url_for('profile_photo'))
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
            # collection.update_one({"username": username}, {"$set": {"Auth_token": hashed_token}})
            collection.update_one(
                {"username": username},
                {
                    "$set": {
                        "Auth_token": hashed_token,
                        "active_time": 0,
                        "inactive_time": 0
                    }
                }
            )
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
    username = session.get("username")
    if username:
        collection.update_one(
            {'username': username},
            {'$set': {'active_time': 0, 'inactive_time': 0}}
        )
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
        security1 = request.form['security1']
        security2 = request.form['security2']

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
        # user_data = {
        #     'username': username,
        #     'hash_password': hashed_password,
        #     'salt': salt,
        #     'security1': security1,
        #     'security2': security2
        # }
        # add active_time and inactive_time init
        user_data = {
            'username': username,
            'hash_password': hashed_password,
            'salt': salt,
            'security1': security1,
            'security2': security2,
            'active_time': 0,
            'inactive_time': 0
        }
        collection.insert_one(user_data)
        flash('Registration successful!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        username = request.form['username']
        security1 = request.form['security1']
        security2 = request.form['security2']
        password_1 = request.form['password_1']
        password_2 = request.form['password_2']

        if password_1 != password_2:
            flash('Password did not match', 'error')
            return redirect(url_for('verify'))

        is_valid_password, password_message = validate_password(password_1)
        if not is_valid_password:
            flash('Invalid password', 'error')
            return redirect(url_for('verify'))

        my_data = collection.find_one({"username": username})
        if my_data is None:
            flash("Username does not exist!", "error")
            return redirect(url_for('verify'))

        if not (my_data["security1"] == security1 and my_data["security2"] == security2):
            flash("No match", "error")
            return redirect(url_for('verify'))

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_1.encode('utf-8'), salt)

        collection.update_one({"username": username}, {"$set": {"hash_password": hashed_password}})
        return redirect(url_for('login'))
    return render_template('checkSecurity.html')


socketio = SocketIO(app)


# Define WebSockets
@app.route('/page3', methods=['GET'])
def page3():
    page_posts = list(posts_collection.find())
    if page_posts.__len__() > 0:
        page_posts = list(reversed(page_posts))
    return render_template("post.html", posts=page_posts)


def create_single_post(username, content):
    post_data = {
        "username": username,
        "content": content,
        "created_at": datetime.now()
    }
    result = posts_collection.insert_one(post_data)
    post_data['_id'] = str(result.inserted_id)
    print(f"Post with ID: {post_data['_id']}")
    return post_data


@socketio.on('create_post')
def handle_create_post(raw_data):
    print("Received create_post with:", raw_data)
    username = session.get('username')

    if not username:
        print("No username found .")
        return
    escape_content = escape(raw_data['content'])
    post_data = create_single_post(username, escape_content)
    post_data['liked_by'] = []
    post_data['disliked_by'] = []

    if isinstance(post_data['created_at'], datetime):
        post_data['created_at'] = post_data['created_at'].isoformat()

    emit('post_created', {
        'status': 'success',
        'message': 'Post created successfully!',
        'post': post_data
    }, broadcast=True)


@socketio.on('like_post')
def handle_like_post(data):
    post_id = data.get('post_id')
    username = session.get('username')

    if not username or not post_id:
        emit('like_response', {'result': 'error', 'message': 'Missing post ID or not logged in.'}, broadcast=False)
        return

    post_id = ObjectId(post_id)
    post = posts_collection.find_one({"_id": post_id})

    if not post:
        emit('like_response', {'message': 'Post not found.'}, broadcast=False)
        return

    if username in post.get('liked_by', []):
        emit('like_response', {'result': 'error', 'message': 'You have already liked this post.'}, broadcast=False)
        return
    # if username in post.get('liked', []):
    #     emit('like_response', {'message': 'You have already liked this post.'}, broadcast=False)
    #     return

    # update_like = posts_collection.update_one(
    #     {"_id": post_id},
    #     {"$addToSet": {"liked": username}, "$inc": {"likes": 1}}
    # )
    #
    #
    # post = posts_collection.find_one({"_id": post_id})
    #
    # if update_like.modified_count:
    #     emit('like_response', {
    #         'result': 'success',
    #         'post': {'_id': str(post_id)},
    #         'total_likes': post.get('likes', 0)
    #     }, broadcast=True)
    # else:
    #     emit('like_response', {'message': 'like fail.'}, broadcast=False)
    update_like = posts_collection.update_one(
        {"_id": post_id},
        {
            "$addToSet": {"liked_by": username},
            "$inc": {"likes": 1}
        }
    )

    post = posts_collection.find_one({"_id": post_id})

    if update_like.modified_count:
        emit('like_response', {
            'result': 'success',
            'post': {'_id': str(post_id)},
            'total_likes': post.get('likes', 0),
            'liked_by': post.get('liked_by', [])
        }, broadcast=True)
    else:
        emit('like_response', {'message': 'like fail.'}, broadcast=False)


@socketio.on('dislike_post')
def handle_dislike_post(data):
    post_id = data.get('post_id')
    username = session.get('username')

    if not username or not post_id:
        emit('dislike_response', {'message': 'Missing post ID or not logged in.'}, broadcast=False)
        return

    post_id = ObjectId(post_id)
    post = posts_collection.find_one({"_id": post_id})

    if not post:
        emit('dislike_response', {'message': 'Post not found.'}, broadcast=False)
        return

    if username in post.get('disliked_by', []):
        emit('dislike_response', {'result': 'error', 'message': 'You have already disliked this post.'})
        return
    # if username in post.get('disliked', []):
    #     emit('dislike_response', {'message': 'You have already disliked this post.'}, broadcast=False)
    #     return

    # update_dislike = posts_collection.update_one(
    #     {"_id": post_id},
    #     {"$addToSet": {"disliked": username}, "$inc": {"dislikes": 1}}
    # )
    #
    #
    # if update_dislike.modified_count:
    #     post = posts_collection.find_one({"_id": post_id})
    #     emit('dislike_response', {
    #         'result': 'success',
    #         'post': {'_id': str(post_id)},
    #         'total_dislikes': post['dislikes']
    #     }, broadcast=True)
    # else:
    #     emit('dislike_response', {'message': 'dislike fail.'}, broadcast=False)
    update_dislike = posts_collection.update_one(
        {"_id": post_id},
        {
            "$addToSet": {"disliked_by": username},
            "$inc": {"dislikes": 1}
        }
    )

    post = posts_collection.find_one({"_id": post_id})

    if update_dislike.modified_count:
        emit('dislike_response', {
            'result': 'success',
            'post': {'_id': str(post_id)},
            'total_dislikes': post.get('dislikes', 0),
            'disliked_by': post.get('disliked_by', [])
        }, broadcast=True)
    else:
        emit('dislike_response', {'message': 'dislike fail.'}, broadcast=False)


# # post page with socket

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


@socketio.on('update_activity')
def handle_activity(data):
    username = session.get('username')
    if not username:
        return

    # current_time = datetime.now()
    update_time = data['duration'] / 1000
    # check if it active
    if data['type'] == 'active':
        collection.update_one({'username': username}, {
            '$inc': {'active_time': update_time}
        })
        # check if it inactive
    elif data['type'] == 'inactive':
        collection.update_one({'username': username}, {
            '$inc': {'inactive_time': update_time}
        })
    # update time
    user = collection.find_one({'username': username})
    emit('activity_update', {
        'active_time': user['active_time'],
        'inactive_time': user['inactive_time']
    }, broadcast=True)


@app.after_request
def set_response_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000, debug=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
