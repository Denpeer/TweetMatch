import sys
from App.data.sgd import predict, checkData
from App.data.synonyms import get_suggestions
from flask import render_template, flash, redirect
from App import app
from .forms import LoginForm




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
@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])
@app.route('/bootstrap',methods=['GET','POST'])
def bootstrap():
	form = LoginForm()
	subtitle = 'How to use TweetMatch'
	pickleFile = 'dumped_classifier.pkl'
	tweetData = 'tweets.csv'
	trumpiness = 0
	checkData(tweetData,pickleFile)
	if form.validate_on_submit():
         subtitle = 'Tweet results'
         prediction = predict(form.tweet.data,pickleFile)
         trumpiness = prediction[2]*100
         if prediction[0] == "1":
             flash('You tweet like: Donald Trump')
         else:
             flash('You don\'t tweet like: Donald Trump')
         scores, keylist = get_suggestions(form.tweet.data,pickleFile)
         suggestions = []
         for key in keylist:
             if key > prediction[2]:
                 suggestions.append(scores[key])
         for suggestion in suggestions:
               print(suggestion)
	else:
		flash('''
			Using TweetMatch is simple! Start by typing your tweet in the box above. 
			Once you're ready to tweet press "Tweet" and TweetMatch will analyse your tweet for you.
			''')

	return render_template('blog/index.html',subtitle=subtitle,form=form,trumpiness=trumpiness)