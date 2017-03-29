import sys
from App.data.sgd import predict
from flask import render_template, flash, redirect
from App import app
from .forms import LoginForm



@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Dennis'}  # fake user
    return render_template("blog/index.html",title='Home',user=user)


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

@app.route('/bootstrap',methods=['GET','POST'])
def bootstrap():
	form = LoginForm()
	subtitle = 'How to use TweetMatch'
	if form.validate_on_submit():
		subtitle = 'Tweet results'
		picklefile = 'dumped_classifier.pkl'
		prediction = predict(form.tweet.data,picklefile)
		if prediction == "1":
			flash('You tweet like: Donald Trump')
		else:
			flash('You don\'t tweet like: Donald Trump')
	else:
		flash('''
			Using TweetMatch is simple! Start by typing your tweet in the box above. 
			Once you're ready to tweet press "Tweet" and TweetMatch will analyse your tweet for you.
			''')

	return render_template('blog/index.html',subtitle=subtitle,form=form)