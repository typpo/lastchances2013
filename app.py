import os
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
  created_at = db.Column(db.DateTime, default=db.func.now)
  chooser = db.Column(db.String, nullable=False)
  chosen = db.Column(db.String, nullable=False)
  __table_args__ = (db.UniqueConstraint('chooser', 'chosen', name='_chooser_chosen_uc'),)

@app.before_request
def verify_login():
  if request.endpoint != 'flask_cas.login' and ('user' not in session):
    return redirect(url_for('flask_cas.login'))

@app.route('/')
def index(name=None):
  return render_template('index.html')

@app.route('/chosen', methods=['GET'])
def chosen():
  print session
  chosens = Selection.query.filter(Selection.chooser == session['user']['netid']).all()

@app.route('/choose', methods=['POST'])
def choose():
  selection = Selection(chooser=session['user']['netid'], chosen=request.form['choice'])
  db.session.add(selection)

  try:
    db.session.commit()
  except:
    return "DUP"

  return "OK"

if __name__ == '__main__':
	app.run(debug=True)
