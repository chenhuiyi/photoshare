######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
from operator import itemgetter
#for image uploading
from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password' # change this to your own password
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	try:
		user.is_authenticated = request.form['password'] == pwd
		return user
	except:
		pass

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')


#Edit by HUIYI CHEN
@app.route("/register", methods=['POST', 'GET'])
def register_user():
	if request.method == 'POST':
		try:
			email=request.form.get('email')
			password=request.form.get('password')

			#By HUIYI CHEN: try to get first name, last name, date of birth
			first_name = request.form.get('first_name')
			last_name = request.form.get('last_name')
			birthday = request.form.get('birthday')

		except:
			print ("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
			return render_template('register.html', supress=True)

		if not email or not password or not first_name or not last_name or not birthday:
			print ("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
			return render_template('register.html', message = "not enough information", supress=True)

		#BY HUIYI CHEN: try to get gender and hometown, if not null

		gender = request.form.get('gender')
		if not gender:
			gender = 0

		try:
			hometown = request.form.get('hometown')
		except:
			hometown = 'NULL'


		cursor = conn.cursor()
		test =  isEmailUnique(email)



		if test:
			print (cursor.execute("INSERT INTO Users (email, password, first_name, last_name, date_of_birth, gender, hometown) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(email, password, first_name, last_name, birthday,gender, hometown)))
			conn.commit()
			#log user in
			user = User()
			user.id = email
			flask_login.login_user(user)
			uid = getUserIdFromEmail(flask_login.current_user.id)
			return render_template('hello.html', name=email, message='Account Created!')
		else:
			print ("email is not unique")
			#Edit by HUIYI CHEN
			return render_template('register.html', supress=False)

	else:
		return render_template('register.html', supress=True)

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

#BY HUIYI CHEN
#begin friend related code
def getUsersFriends(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name, email FROM Users WHERE user_id IN (SELECT userA FROM Befriend_With WHERE userB = '{0}')".format(uid))
	return cursor.fetchall()

#Friends list page
@app.route('/friends')
@flask_login.login_required
def friends_list():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('friends.html', name=flask_login.current_user.id, friendslist=getUsersFriends(uid))


@app.route('/addfriend', methods=['GET', 'POST'])
@flask_login.login_required
def add_friend():
	if request.method == 'POST':
		try:
			friend_email=request.form.get('friend_email')
		except:
			return render_template('addfriend.html')

		if isEmailUnique(friend_email):
			return render_template('addfriend.html', message = "User not exist, try a different one")
		else:
			friend_id = getUserIdFromEmail(friend_email)
			uid = getUserIdFromEmail(flask_login.current_user.id)

			if areFriends(friend_id, uid):
				return render_template('addfriend.html', message = "You are friends already, try a different one")
			elif friend_id == uid:
				return render_template('addfriend.html', message = "No need to add yourself, try a different one")
			else:
				cursor = conn.cursor()
				cursor.execute("INSERT INTO Befriend_With (UserA, UserB) VALUES ('{0}', '{1}')".format(uid, friend_id))
				cursor.execute("INSERT INTO Befriend_With (UserA, UserB) VALUES ('{0}', '{1}')".format(friend_id, uid))
				conn.commit()
				albums = getAlbumFromUid(uid)
				return render_template('hello.html', name=flask_login.current_user.id, message="You have a new friend", albums = albums)
	else:

		return render_template('addfriend.html', name=flask_login.current_user.id)

def areFriends(fid, uid):
	cursor = conn.cursor()
	if cursor.execute("SELECT * FROM Befriend_With WHERE userA = '{0}' AND userB = '{1}'".format(fid, uid)):
		return True #fid and uid are already friends
	else:
		return False


@app.route('/searchfriends', methods=['GET','POST'])
@flask_login.login_required
def search_friends():
	if request.method == "POST":
		first_name = request.form.get('first_name')
		last_name = request.form.get('last_name')
		if first_name:
			results = getResults(first_name, 'first_name')
		elif last_name:
			results = getResults(last_name, 'last_name')
		else:
			return render_template('searchfriends.html', name = flask_login.current_user.id, message="empty input, try a different one")

		if results:
			return render_template('addfriend.html', name = flask_login.current_user.id, results = results)
		else:
			return render_template('searchfriends.html', name = flask_login.current_user.id, message="User not exist, try a different one")

	else:
		return render_template('searchfriends.html', name = flask_login.current_user.id)

def getResults(name, attribute):
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name, email FROM Users WHERE {0} = '{1}'".format(attribute, name))
	return cursor.fetchall()
#end friend related code


#BY HUIYI CHEN
#begin user activity code
@app.route('/contribution')
def contribution():
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Users")
	users = cursor.fetchall()
	contribution = []
	for user_id in users:
		photos = len(getUsersPhotos(user_id[0]))
		comments = getUsersComments(user_id[0])
		total = photos + comments
		user_email = getUserEmailFromID(user_id[0])
		contribution.append((user_email, total))
	contribution = sorted(contribution, key = itemgetter(1), reverse = True)
	contribution = contribution[:10]
	print(contribution)
	return render_template('contribution.html', contributors = contribution)

def getUserEmailFromID(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT email FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()[0]

def getUsersComments(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(*) FROM Comments WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()[0]
#end user activity code



#BY HUIYI CHEN
#begin album code

@app.route('/createalbum', methods = ['GET','POST'])
@flask_login.login_required
def create_album():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		album_name = request.form.get('album_name')
		if albumExists(album_name, uid):
			return render_template('createalbum.html', message = "Album exsits, try a different name")
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Albums(user_id, date_of_creation, album_name) VALUES ('{0}', CURRENT_DATE, '{1}')".format(uid, album_name))
		conn.commit()
		albums = getAlbumFromUid(uid)
		return render_template("hello.html", name = flask_login.current_user.id, message = "Album created successfully", albums = albums,tags = getTags())
	else:
		return render_template('createalbum.html')

def getAlbumFromUid(uid):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT album_id, album_name FROM Albums WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()

def albumExists(album_name, uid):
	cursor = conn.cursor()
	if cursor.execute("SELECT * FROM Albums WHERE album_name = '{0}' AND user_id = '{1}'".format(album_name, uid)):
		return True
	else:
		return False

def getAlbumPictures(aid):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id, caption, imgdata FROM Pictures WHERE album_id = '{0}'".format(aid))
	return cursor.fetchall()

def getAlbumInformation(aid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_name, date_of_creation, user_id FROM Albums WHERE album_id = '{0}'".format(aid))
	return cursor.fetchone()

@app.route('/album/<aid>')
def album(aid):
	(album_name, date_of_creation, uid) = getAlbumInformation(aid)
	pictures = getAlbumPictures(aid)
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name,email FROM Users WHERE user_id = '{0}'".format(uid))
	(first_name, last_name,email) = cursor.fetchone()
	if email == flask_login.current_user.id:
		auth = True
	else:
		auth = False
	return render_template('album.html', name = flask_login.current_user.id, album_name = album_name, first_name = first_name, last_name = last_name, date_of_creation = date_of_creation, pictures = pictures, album_id = aid, auth = auth)

@app.route('/deletealbum/<aid>')
@flask_login.login_required
def deleteAlbum(aid):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Albums WHERE album_id = '{0}'".format(aid))
	conn.commit()
	uid = getUserIdFromEmail(flask_login.current_user.id)
	albums = getAlbumFromUid(uid)
	return render_template('hello.html', name=flask_login.current_user.id, message="Album has been deleted", albums = albums,tags = getTags())
#end album code


def getTags():
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT word FROM Tags")
	tags = cursor.fetchall()
	return tags



#begin picture code
@app.route('/picture/<pid>')
def picture(pid):
	(uid, caption, imgdata, album_id, likes) = getPictureInformation(pid)
	tags = getPictureTags(pid)
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name, email FROM Users WHERE user_id = '{0}'".format(uid))
	(first_name, last_name, email) = cursor.fetchone()
	conn.commit()
	cursor = conn.cursor()
	cursor.execute("SELECT album_name FROM Albums WHERE album_id = '{0}'".format(album_id))
	album_name = cursor.fetchone()[0]
	conn.commit()
	if email == flask_login.current_user.id:
		auth = True
	else:
		auth = False
	comments = getComments(pid)

	return render_template('picture.html', name = flask_login.current_user.id, caption = caption, imgdata = imgdata, first_name = first_name, last_name = last_name, tags = tags, album_name = album_name, auth = auth, pid = pid, album_id = album_id, comments = comments, likes = likes)

@app.route('/likepicture/<pid>')
def like(pid):
	cursor = conn.cursor()
	cursor.execute("UPDATE Pictures SET likes = likes + 1 WHERE picture_id = '{0}'".format(pid))
	conn.commit()
	return redirect(url_for('picture', pid = pid))

def getPictureInformation(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id, caption, imgdata, album_id,likes FROM Pictures WHERE picture_id = '{0}'".format(pid))
	return cursor.fetchone()

def getComments(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id, comment_text FROM Comments")
	id_comments = cursor.fetchall()
	comments = []
	for comment in id_comments:
		if comment[0] == 0:
			first_name = 'Anonymous'
			last_name = 'User'
		else:
			cursor = conn.cursor()
			cursor.execute("SELECT first_name, last_name FROM Users WHERE user_id = '{0}' AND picture_id = '{1}'".format(comment[0], pid))
			(first_name, last_name) = cursor.fetchone()
		comments.append((first_name, last_name, comment[1]))
	return comments
@app.route('/deletepicture/<pid>')
@flask_login.login_required
def deletePicture(pid):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Pictures WHERE picture_id = '{0}'".format(pid))
	conn.commit()
	uid = getUserIdFromEmail(flask_login.current_user.id)
	albums = getAlbumFromUid(uid)
	return render_template('hello.html', name=flask_login.current_user.id, message="Picture has been deleted", albums = albums,tags = getTags())


def getPictureTags(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT word FROM Tags WHERE picture_id = '{0}'".format(pid))
	return cursor.fetchall()

@app.route('/addtag/<pid>', methods = ['GET', 'POST'])
@flask_login.login_required
def addTag(pid):
	if request.method == 'POST':
		tag= request.form.get('tag')
		if tagExists(tag, pid):
			return render_template('addtag.html', message = "Tag exsits, try a different one", pid=pid)
		if ' ' in tag:
			return render_template('addtag.html', message = "Tag must be a single word", pid=pid)
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Tags(word, picture_id) VALUES ('{0}', '{1}')".format(tag, pid))
		conn.commit()
		return redirect(url_for('picture', pid=pid))
	else:
		return render_template('addtag.html', pid = pid)

def tagExists(tag, pid):
	cursor = conn.cursor()
	if cursor.execute("SELECT * FROM Tags WHERE word = '{0}' AND picture_id = '{1}'".format(tag, pid)):
		return True
	else:
		return False


#end picture code


#begin comment code
@app.route('/comment/<pid>', methods = ['GET', 'POST'])
def comment(pid):
	if request.method == 'POST':
		comment = request.form.get('comment')
		email = flask_login.current_usr.id
		if email:
			uid = getUserIdFromEmail(flask_login.current_user.id)
		else:
			uid = 0
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Comments(user_id, comment_date, comment_text, picture_id VALUES ('{0}', CURRENT_DATE, '{1}', '{2}')".format(uid, comment, pid))
		conn.commit()
		return redirect(url_for('picture', pid=pid))
	else:
		return render_template('comment.html', pid = pid)

#end comment code



#begin view tags code
@app.route('/myphotosbytag/<tag>')
@flask_login.login_required
def myPhotosByTag(tag):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor.execute("SELECT Pictures.picture_id, Pictures.caption, Pictures.imgdata  FROM Tags INNER JOIN Pictures ON Tags.picture_id = Pictures.picture_id WHERE word = '{0}' AND Pictures.user_id = '{1}'".format(tag, uid))
	pictures = cursor.fetchall()
	return render_template('tags.html', pictures = pictures, tag = tag)

@app.route('/photosbytag/<tag>')
def photosByTag(tag):
	cursor = conn.cursor()
	cursor.execute("SELECT Pictures.picture_id, Pictures.caption, Pictures.imgdata  FROM Tags INNER JOIN Pictures ON Tags.picture_id = Pictures.picture_id WHERE word = '{0}'".format(tag))
	pictures = cursor.fetchall()
	return render_template('tags.html', pictures = pictures, tag = tag)

def getUserNameFromUid(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()

def getAlbumName(aid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_name FROM Users WHERE album_id = '{0}'".format(aid))
	return cursor.fetchone()[0]
#end view tags code


@app.route('/profile')
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	albums = getAlbumFromUid(uid)
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile", albums = albums,tags = getTags())

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload/<aid>', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file(aid):
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')

		photo_data = base64.standard_b64encode(imgfile.read())
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Pictures (imgdata, user_id, caption, album_id, likes) VALUES ('{0}', '{1}', '{2}', '{3}', 0)".format(photo_data,uid, caption, aid))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', albums=getAlbumFromUid(uid), tags = getTags())

		# return render_template('upload.html', aid = aid, message = "Only allow file type: png, jpg, jpeg, gif")
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html', aid = aid)
#end photo uploading code




#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare', tags = getTags())



if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
