from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea

class LoginForm(Form):
    tweet = StringField('tweet', validators=[DataRequired()])

class TweetForm(Form):
    tweet = StringField('tweet', widget=TextArea(),validators=[DataRequired()])
