import os
import json
import requests
from datetime import datetime
from flask import Flask, request, redirect, session, url_for, render_template, g
from flask_cas import *
from flask.ext.sqlalchemy import SQLAlchemy
import random
from string import hexdigits

app = Flask(__name__)
app.register_blueprint(flask_cas)
app.config["SECRET_KEY"] = os.environ.get('COOKIE_SECRET', ''.join(random.choice(hexdigits) for _ in range(30)))
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///lc.db'
db = SQLAlchemy(app)

class Commitment(db.Model):
  __tablename__ = 'commitment'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.DateTime, default=db.func.now())

  chooser = db.Column(db.String, db.ForeignKey("user.net_id"), nullable=False)
  coupleid_hash = db.Column(db.String, nullable=False)

  match = db.Column(db.String, default=None)

  __table_args__ = (db.UniqueConstraint('chooser', 'coupleid_hash', name='_chooser_coupleid_hash_uc'),)

class User(db.Model):
  __tablename__ = 'user'
  name = db.Column(db.String, nullable=False)
  net_id = db.Column(db.String, primary_key=True)
  public_key = db.Column(db.String, nullable=False)
  encrypted_private_key = db.Column(db.String, nullable=False)

def error_json(text):
  return json.dumps({'error': text})

@app.before_request
def verify_login():
  if '/static/' in request.path:
    return

  if request.endpoint != 'flask_cas.login' and ('user' not in session):
    return redirect(url_for('flask_cas.login'))

  if 'user' in session:
    g.user = User.query.get(session['user']['netid'])
    if (g.user is None) and (request.path != '/register'):
      return render_template('register.html')

@app.route('/')
def index(name=None):
  private_key = g.user.encrypted_private_key
  return render_template('index.html', private_key=private_key)

@app.route('/register', methods=['POST'])
def register():
  new_user = User(name=request.form['name'], \
                  net_id = session['user']['netid'], \
                  encrypted_private_key=request.form['encrypted_private_key'], \
                  public_key=request.form['public_key'])
  db.session.add(new_user)

  try:
    db.session.commit()
  except:
    return error_json("User already registered!"), 402

  return json.dumps({'success': True})
  return redirect(url_for('index'))

@app.route('/chosen', methods=['GET'])
def chosen():
  #TODO
  return json.dumps([])

@app.route('/participants', methods=['GET'])
def participants():
  users = map(lambda u: {'name': u.name, 'public_key': u.public_key}, User.query.all())
  return json.dumps(users)


@app.route('/matches', methods=['GET'])
def matches():
  results = Commitment.query.filter(Commitment.chooser == g.user.net_id).filter(Commitment.match != None).all()
  results = map(lambda r: r.match, results)
  return json.dumps(results)

@app.route('/unchoose', methods=['POST'])
def unchoose():
  #TODO
  return json.dumps({'deleted':'deleted'})

@app.route('/choose', methods=['POST'])
def choose():
  commitment = Commitment(chooser=g['user'].net_id, \
                          coupleid_hash=request.form['coupleid_hash'], \
                          match=None)
  db.session.add(commitment)

  try:
    db.session.commit()
  except:
    return error_json("Could not add commitment"), 402

def compute_matches():
  commitments = Commitmennt.query.all()
  for commitment in commitments:
    opposite = Commitment.query \
                         .filter(Commitment.coupleid_hash == commitment.coupleid_hash) \
                         .filter(Commitment.chooser != commitment.chooser).all()
    if len(opposite) > 0:
      commitment.match = True
      db.session.add(commitment)
  db.session.commit()


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
