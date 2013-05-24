import os
import json
import requests
from datetime import datetime
from flask import Flask, request, redirect, session, url_for, render_template
from flask_cas import *
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.register_blueprint(flask_cas)
app.config["SECRET_KEY"] = "a^sci^21%02%92"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///test.db'

db = SQLAlchemy(app)

class Selection(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.DateTime, default=db.func.now())
  chooser = db.Column(db.String, nullable=False)
  chosen = db.Column(db.String, nullable=False)
  __table_args__ = (db.UniqueConstraint('chooser', 'chosen', name='_chooser_chosen_uc'),)

def get_user(netid):
  users = requests.get('dnd.hackdartmouth.org', params={'uid': netid}).json
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
  results = Selection.query.filter(Selection.chooser == session['user']['netid']).all()
  results = map(lambda n: n.chosen, results)
  return json.dumps(results)
  
@app.route('/choose', methods=['POST'])
def choose():
  chooser_user = get_user(session['user']['netid'])
  if chooser_user is None:
    return error_json("Could not find logged in user. Please contact us."), 404

  chosen_user = get_user(request.form['choice'])
  if chosen_user is None:
    return error_json("Could not find selected user."), 404
  
  selection = Selection(chooser=chooser_user.netid, chosen=chosen_user.netid)
  db.session.add(selection)

  try:
    db.session.commit()
  except:
    return error_json("User already selected."), 404

  return json.dumps({'netid':chosen_user.netid})

if __name__ == '__main__':
	app.run(debug=True)
