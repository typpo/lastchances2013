import datetime
from flask import url_for
from app import db

class Student(db.Document):
    created_at = datetime.datetime.now
    name = ""
    slug = ""
    email = ""
    choices = []
    #created_at = db.DateTimeField(default=datetime.datetime.now)
	#name = db.StringField(max_length=1000, required=True)
	#slug = db.StringField(max_length=255, required=True)
	#email = db.StringField(required=True)
	#choices = db.ListField(db.EmbeddedDocumentField('Choice'))

    def get_absolute_url(self):
		return url_for('student',kwargs={"slug": self.slug})

    def __unicode__(self):
		return self.name

    meta = {
		'allow_inheritance': True,
        'indexes': ['-name','slug'],
        'ordering': ['-name']
    }

class Choice(db.EmbeddedDocument):
    name = ""
    email = ""
    hint = ""
    #choice_name = db.StringField(max_length=1000, required=True)
	#choice_email = db.StringField(max_length=1000)
	#drop_a_hint = db.StringField(max_length=1000)
