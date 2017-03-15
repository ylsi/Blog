from __future__ import with_statement
import sqlite3
import os
from flask import Flask, request, session, g, flash
from flask import redirect, url_for, abort, render_template
from contextlib import closing

DATABASE = os.path.join(os.getcwd(), 'blog.db')
DEBUG = True
SECRET_KEY = os.urandom(24)
USERNAME = 'admin'
PASSWORD = 'root'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
	return sqlite3.connect(app.config['DATABASE'])
	
def init_db():
	with closing(connect_db()) as db:
		with open('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()
		
@app.before_request
def befor_request():
	g.db = connect_db()
	
@app.teardown_request
def teardown_request(exception):
	g.db.close()
	
@app.route('/')
def index():
	cur = g.db.execute('select title, text from entries order by id desc')
	entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
	return render_template('index.html', entries=entries)
	
@app.route('/add', methods=['POST', 'GET'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	g.db.execute('insert into entries (title, text) values (?, ?)', [request.form['title'], request.form['text']])
	g.db.commit()
	#flash('Nex entry was successsfully posted')
	return redirect(url_for('index'))
	
@app.route('/login', methods=['POST', 'GET'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] !=  app.config['USERNAME']:
			error = 'Invalid usernmae'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('index'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('index'))
	
if __name__ == '__main__':
	app.run()