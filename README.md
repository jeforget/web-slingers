# Additional functionality
We have added the additional feature of password reset. As users, there is a high chance that we might not remember the password to our account. 
Well fret not, because this feature allows you to change your password as long as you have the answers to the security questions asked during registration.

Testing Procedure:
1. Start your server using docker compose up
2. Navigate to http://localhost:8080/
3. Register an account and save the answers to the security questions
4. Go to the Login Page and then click on Forgot Password?
5. Attempt to change the password using the registered username and passwords that do not match. Ensure that a message stating that the passwords do not match is displayed.
6. Attempt to change the password with the registered username and incorrect answers to security questions. Ensure that a message stating that there is no match.
7. Then change the password using the registered username and correct answers to the security questions. Ensure that you are redirected to the login page.
8. Login using the username and the new password. 
9. Ensure that you are redirected to the Logged_in page and you can now post.

# A note to whoever is grading this:
We sadly could not get https working with websockets, and have two (same IP just one is HTTP and one is HTTPS) "deployed" versions.

This link is the HTTP deployment. This one has obj 1 and obj 2: http://143.198.180.44:8990/

This link is to a secure version that should be using HTTPS. This one has obj 1 and obj 3 set up. The chat does not function however, so we cannot use this one: https://postboard.win/

# DO NOT PUSH TO OR MODIFY MAIN
I wanted to go over this in the meeting but to avoid us overwriting each other's stuff you need to **CREATE A BRANCH OFF OF DEVELOP** and work from there. Then once you're done, merge with develop! We should **NOT** be touching main until we're done and have the bugs worked out! Only then will we merge develop with main.

# Repo Layout:
This new layout should allow us to add without overwriting each other's files.

# Backend
app.py is the main backend file, essentially our version of server.py. The util folder is where we'll put supporting backend files. 

# HTML
The templates folder holds our HTML files, my home file is called "index.html", and "base.html" is the base file that the other HTML files will extend.

On that note, I'm trying to utilize some inheritance with the HTML files. To my understanding, this allows us to not have to type the same HTML for every page we want to make. The "base.html" file has the header and doctype shared by all files, so that when you make a new one you can just put "{% extends 'base.html' %}" at the top. Look over my index.html and base.html to get an understanding.

# The Static Folder
This folder holds all of our "static" frontend files, within this folder, there are currently 3 folders; css, js, and images.

images is just where we can put our images that we're using.

css is where we'll keep our css files, I've put "home_" in front of all of the files that I use, I'm hoping you guys will also use a prefix of your own just so things don't get mixed up.

js holds our JavaScript files. Again, mine has a "home_" prefix to avoid confusion once we start adding to the folder.
