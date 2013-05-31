import os
import json
import requests
from datetime import datetime
from flask import Flask, request, redirect, session, url_for, render_template
from flask_cas import *
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.register_blueprint(flask_cas)
app.config["SECRET_KEY"] = os.environ['COOKIE_SECRET']
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///lc.db'
db = SQLAlchemy(app)

class Selection(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.DateTime, default=db.func.now())
  chooser = db.Column(db.String, nullable=False)
  chosen = db.Column(db.String, nullable=False)
  __table_args__ = (db.UniqueConstraint('chooser', 'chosen', name='_chooser_chosen_uc'),)

def get_user(netid):
  users = requests.get('http://dnd.hackdartmouth.org', params={'uid': netid}).json()
  if len(users) < 1:
    return None
  return users[0]

def error_json(text):
  return json.dumps({'error': text})

@app.before_request
def verify_login():
  if request.endpoint != 'flask_cas.login' and ('user' not in session):
    return redirect(url_for('flask_cas.login'))

@app.route('/')
def index(name=None):
  return render_template('index.html')

@app.route('/chosen', methods=['GET'])
def chosen():
  chooser_user = get_user(session['user']['netid'])
  results = Selection.query.filter(Selection.chooser == chooser_user['uid']).all()
  results = map(lambda n: n.chosen, results)
  return json.dumps(results)

@app.route('/unchoose', methods=['POST'])
def unchoose():
  try:
    chooser_user = get_user(session['user']['netid'])
    selection = Selection.query.filter(Selection.chooser == chooser_user['uid']).filter(Selection.chosen == request.form['choice']).first()
    db.session.delete(selection)
    db.session.commit()
    return json.dumps({'deleted':'deleted'})
  except:
    return json.dumps({'deleted':'error'}), 401

@app.route('/choose', methods=['POST'])
def choose():
  chooser_user = get_user(session['user']['netid'])
  if chooser_user is None:
    return error_json("Could not find logged in user. Please contact us."), 401

  chosen_user = get_user(request.form['choice'])
  if chosen_user is None:
    return error_json("Could not find selected user."), 404
  
  selection = Selection(chooser=chooser_user['uid'], chosen=chosen_user['uid'])
  db.session.add(selection)

  try:
    db.session.commit()
  except:
    return error_json("User already selected."), 402

  return json.dumps({'chosen':chosen_user['uid']})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
