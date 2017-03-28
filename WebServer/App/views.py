from flask import render_template, flash, redirect
from App import app
from .forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Dennis'}  # fake user
    return render_template("index.html",title='Home',user=user)


@app.route('/tweet',methods=['GET','POST'])
def tweet():
	form = LoginForm()
	if form.validate_on_submit():
		if "china" in form.tweet.data.lower():
			flash('You tweet like: Donald Trump')
		else:
			flash('You don\'t tweet like: Donald Trump')

	return render_template('tweet.html',
							title="Tweet",
							form=form)