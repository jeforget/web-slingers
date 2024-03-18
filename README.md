# DO NOT PUSH TO OR MODIFY MAIN
I wanted to go over this in the meeting but to avoid us overwriting each other's stuff you need to **CREATE A BRANCH OFF OF DEVELOP** and work from there. Then once you're done, pull from develop, then merge with develop! We should **NOT** be touching main until we're done and have the bugs worked out!

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
