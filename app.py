import ldap
from flask import Flask, request, redirect, session, url_for, render_template
from flask.ext.mongoengine import MongoEngine
from flask_cas import flask_cas


app = Flask(__name__)
app.register_blueprint(flask_cas)
app.config["MONGODB_DB"] = "my_lastChances"
app.config["SECRET_KEY"] = "a^sci^21%02%92"

db = MongoEngine(app)

def register_blueprints(app):
	from views import students
	app.register_blueprint(students)

register_blueprints(app)

@app.route("/")
def index():
	return render_template('index.html')

if __name__ == '__main__':
	app.run()
