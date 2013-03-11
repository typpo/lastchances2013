import os
import ldap
from flask import Flask, request, redirect, session, url_for, render_template
from pymongo import Connection
from urlparse import urlparse
from flask_cas import *
from forms import LastChancesForm

app = Flask(__name__)
app.register_blueprint(flask_cas)
app.config["MONGODB_DB"] = "lastChances"
app.config["SECRET_KEY"] = "a^sci^21%02%92"

MONGO_URL = os.environ.get('MONGOHQ_URL')

if MONGO_URL:
# Get a connection
    connection = Connection(MONGO_URL)
# Get the database
    db = connection['lastChances']
else:
# Not on an app with the MongoHQ add-on, do some localhost action
    connection = Connection('localhost', 27017)
    db = connection['MyDB']

chances = db.lastChances

"""
def register_blueprints(app):
	from views import students
	app.register_blueprint(students)

register_blueprints(app)
"""

@app.route('/')
def index(name=None):
    #print "index"
    return render_template('index.html')

@app.route('/choose',methods=['GET','POST'])
def makeChoices():
    if request.method == 'GET':
        form = LastChancesForm()
        return render_template('choose.html', form=form)
    else:
        entry = {"name":session['user']['name'],
                 "Choice1":request.form['choice1'],
                 "Choice2":request.form['choice2']
                 }
        chances.insert(entry)
        return "Congratulations, your entries have been submitted. Stay tuned."

if __name__ == '__main__':
	app.run(debug=True)
