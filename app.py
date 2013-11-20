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
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///matchmaking.db'
db = SQLAlchemy(app)

class Commitment(db.Model):
  __tablename__ = 'commitment'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.DateTime, default=db.func.now())

  chooser_id = db.Column(db.String, db.ForeignKey("user.net_id"), nullable=False)
  chooser = db.relationship("User", backref=db.backref('commitments'), foreign_keys=[chooser_id])

  encrypted_name = db.Column(db.String, nullable=False)

  coupleid_hash = db.Column(db.String, nullable=False)

  match_id = db.Column(db.String, db.ForeignKey("user.net_id"), default=None)
  match = db.relationship("User", foreign_keys=[match_id])

  __table_args__ = (db.UniqueConstraint('chooser_id', 'coupleid_hash', name='_chooser_id_coupleid_hash_uc'),)

class User(db.Model):
  __tablename__ = 'user'
  name = db.Column(db.String, nullable=False)
  net_id = db.Column(db.String, primary_key=True)
  public_key_bits = db.Column(db.String, nullable=False)
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
  num_matches = Commitment.query.filter(Commitment.chooser == g.user).filter(Commitment.match != None).count()
  return render_template('index.html', private_key=json.dumps(private_key), num_matches=num_matches)

@app.route('/register', methods=['POST'])
def register():
  print session
  new_user = User(name=session['user']['name'], \
                  net_id = session['user']['netid'], \
                  encrypted_private_key=request.form['encrypted_private_key'], \
                  public_key_bits=request.form['public_key_bits'])
  db.session.add(new_user)

  try:
    db.session.commit()
  except:
    return error_json("User already registered!"), 402

  return json.dumps({'success': True})
  return redirect(url_for('index'))

@app.route('/chosen', methods=['GET'])
def chosen():
  commitments = Commitment.query.filter(Commitment.chooser == g.user).filter(Commitment.match == None).all()
  commitments = map(lambda c: {'encrypted_name': c.encrypted_name, 'coupleid_hash' : c.coupleid_hash}, commitments)
  return json.dumps(commitments)

@app.route('/participants', methods=['GET'])
def participants():
  users = map(lambda u: {'name': u.name, 'public_key_bits': u.public_key_bits}, User.query.all())
  return json.dumps(users)


@app.route('/matches', methods=['GET'])
def matches():
  results = Commitment.query.filter(Commitment.chooser == g.user).filter(Commitment.match != None).all()
  results = map(lambda r: {'name': r.match.name }, results)
  return json.dumps(results)

@app.route('/unchoose', methods=['POST'])
def unchoose():
  commitment = Commitment.query.filter(Commitment.chooser == g.user).filter(Commitment.coupleid_hash == request.form['coupleid_hash']).filter(Commitment.match == None).first()
  if commitment == None:
    return error_json("Commitment does not exist"), 404

  db.session.delete(commitment)

  try:
    db.session.commit()
  except:
    return error_json("Could not remove commitment"), 401

  return json.dumps({'deleted':'deleted'})

@app.route('/choose', methods=['POST'])
def choose():
  commitment = Commitment(chooser=g.user, \
                          coupleid_hash=request.form['coupleid_hash'], \
                          encrypted_name=request.form['encrypted_name'], \
                          match=None)
  db.session.add(commitment)

  try:
    db.session.commit()
  except:
    return error_json("Could not add commitment"), 402

  return "Success"

def compute_matches():
  commitments = Commitment.query.all()
  for commitment in commitments:
    opposite = Commitment.query \
                         .filter(Commitment.coupleid_hash == commitment.coupleid_hash) \
                         .filter(Commitment.chooser_id != commitment.chooser_id).all()
    if len(opposite) > 0:
      commitment.match_id = opposite[0].chooser_id
      db.session.add(commitment)
  db.session.commit()


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
