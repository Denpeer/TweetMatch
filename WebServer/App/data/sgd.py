import sys
import csv
import numpy as np
import scipy
import _pickle
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline, FeatureUnion
from math import ceil
from sklearn import metrics
from textstat.textstat import textstat
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import normalize
from App.data.tweet_mining import downloadTweets

#Feature transformer class for pipeline
class extraFeature(BaseEstimator, TransformerMixin):
    def __init__(self, func):
        self.func = func
    
    #Calculate feature metric (e.g. Flesch-Kincaid reading ease) for each sentence in the input and normalize the scores
    def transform(self, X, y=None):
        #Use function passed in pipeline
        ret = normalize(np.array([float(self.func(sentence)) for sentence in X]).reshape(-1,1))

        return ret
    
    def fit(self, X, y=None):
        return self

def removeURLs(urls,tweets):
    # Remove all tweets
    for idx, val in enumerate(zip(urls,tweets)):
        if(urls[idx]!=''):
            urlList = urls[idx].split(', ')
            resultwords  = [word for word in val[1].split() if word not in urlList]
            tweets[idx] = ' '.join(resultwords)
    return tweets

def getText():
    # Read tweets from csv
    with open('tweets.csv','rt') as csvfile:
        reader = csv.DictReader(csvfile)
        tweet_all = [(row['tweet_text'],row['politician_name'],row['tweet_by_trump'],row['tweet_urls']) for row in reader]
        tweet_text = [x[0] for x in tweet_all]
        tweet_urls =  [x[3] for x in tweet_all]
        removeURLs(tweet_urls,tweet_text)
        return tweet_all

#Return pipeline with the combined features of the tdidf and reading ease score and Stochastic Gradient Descent Classifier
def train(X,Y):
    text_clf = Pipeline([
                         ('features',FeatureUnion([
                                                   ('words',Pipeline([
                                                                      ('vect', CountVectorizer(ngram_range=(1,2))),
                                                                      ('tfidf', TfidfTransformer(use_idf=True))
                                                                      ])),
                                                   ('fleshReadingEase',extraFeature(textstat.flesch_reading_ease)),
                                                   ('smogIndex',extraFeature(textstat.smog_index)),
                                                   ('colemanLiauIndex',extraFeature(textstat.coleman_liau_index)),
                                                   ('fleschKincaidGrade',extraFeature(textstat.flesch_kincaid_grade)),
                                                   ('automatedReadibilityIndex',extraFeature(textstat.automated_readability_index)),
                                                   ('daleChallReadability',extraFeature(textstat.dale_chall_readability_score)),
                                                   ('difficultWords',extraFeature(textstat.difficult_words)),
                                                   ('linsearWriteFormula',extraFeature(textstat.linsear_write_formula)),
                                                   ('gunningFog',extraFeature(textstat.gunning_fog))
                                                   ])),
                         ('clf', SGDClassifier(learning_rate='optimal',eta0=0.001,class_weight='balanced',loss='modified_huber', penalty='l2',alpha=1e-3, n_iter=5, random_state=42))
    ])
    
    return text_clf.fit(X, Y)

def setup(pickleFile):
    # Read relevant rows
    tweet_all = getText()
    tweet_text = [x[0] for x in tweet_all]
    politician_name = [x[1] for x in tweet_all]
    tweet_by_trump = [x[2] for x in tweet_all]
    
    #Split the data into around 80% training data and 20% test data
    p = np.random.permutation(len(tweet_all))
    split = ceil(len(tweet_all)*0.8)
    tweet_text_train = [tweet_text[x] for x in p[:split]]
    politician_name_train = [politician_name[x] for x in p[:split]]
    tweet_by_trump_train = [tweet_by_trump[x] for x in p[:split]]
    
    tweet_text_test = [tweet_text[x] for x in p[split:]]
    politician_name_test = [politician_name[x] for x in p[split:]]
    tweet_by_trump_test = [tweet_by_trump[x] for x in p[split:]]

    # Train the model
    text_clf = train(tweet_text_train, tweet_by_trump_train)
    

    # Validate the model
    predicted = text_clf.predict(tweet_text_test)
    #confidence = text_clf.decision_function(tweet_text_test)
    print("Classification report:\n"+metrics.classification_report(tweet_by_trump_test, predicted,target_names=('Trump','Not Trump')))

    # pickle classifier (save to disk)
    with open(pickleFile, 'wb') as fid:
        _pickle.dump(text_clf, fid)


    return text_clf

# predicts a tweet represented as a string using a pickled classifier
def predict(tweet,pickleFile):

    # if pickled model is not available under given filename, retrain and create it
    if (os.path.isfile(pickleFile) == False):
        return trainAndPredict(tweet,pickleFile)

    # unpickling can result in an AttributeError when not pickled in flask, retrain and repickle in this case.
    try:
        # unpickle classifier
        with open(pickleFile, 'rb') as fid:
            text_clf = _pickle.load(fid)
    
    except AttributeError as e:
        print(e + ": model pickled outside of flask.\n Retraining model")
        return trainAndPredict(tweet,pickleFile)
    
    else:
        prediction = text_clf.predict([tweet])[0]
        print("Result: " + tweet + " = " + prediction)
        print('probability of trump tweet: ')
        print(text_clf.predict_proba([tweet])[0][1])
        print('probability that it\'s not a trump tweet') 
        print(text_clf.predict_proba([tweet])[0][0])
        return [prediction,text_clf.predict_proba([tweet])[0][0],text_clf.predict_proba([tweet])[0][1]]

# checks if necessary data is present, download it when it's not. return true after data is retrieved.
def checkData(tweetData,pickleFile):
    if (os.path.isfile(tweetData) == False):
        downloadTweets(tweetData)

    # testtweet can be used in this case since the value is not actually used. The function just trains the model
    if (os.path.isfile(pickleFile) == False):
        trainAndPredict('testweet',pickleFile)
    else:
        try:
        # unpickle classifier
            with open(pickleFile, 'rb') as fid:
                text_clf = _pickle.load(fid)
    
        except AttributeError as e:
            print(e + ": model pickled outside of flask.\n Retraining model")
            trainAndPredict('testtweet',pickleFile)

    print("current working directory: " + os.getcwd() +"\n"+"Tweet data available on: "+ tweetData + " Pickled model available on: "+ pickleFile)
    return True

# predicts a tweet represented as a string by training from tweets.csv
def trainAndPredict(tweet,pickleFile):

    print("Training the model")
    text_clf = setup(pickleFile)

    print("Done")
    
    return predict(pickleFile)

def main(argv):
    
    print("Training the model")
    text_clf = setup()

    print("Done")
    if (len(argv) == 2):
        print("predicting \""+argv[1]+"\" from Donald Trump")
        print(text_clf.predict(argv)[1])
    
    print(argv[1] + " : " + predict(argv[1]))

if __name__ == "__main__":
    main(sys.argv)


