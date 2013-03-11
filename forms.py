
from flask.ext.wtf import Form, TextField, BooleanField, HiddenField
from flask.ext.wtf import Required

class LastChancesForm(Form):
        choice1 = TextField('choice2')
        choice2 = TextField('choice1')



