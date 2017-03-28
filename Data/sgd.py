import sys
import csv
import numpy as np
import scipy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline, FeatureUnion
from math import ceil
from sklearn import metrics
from textstat.textstat import textstat
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import normalize

#Feature transformer class for pipeline
class extraFeature(BaseEstimator, TransformerMixin):
    def __init__(self, func):
        self.func = func
    
    #Calculate feature metric (e.g. Flesch-Kincaid reading ease) for each sentence in the input and normalize the scores
    def transform(self, X, y=None):
        #Use function passed in pipeline
        ret = [self.func(sentence) for sentence in X]
        ret = np.array(normalize(ret)[0]).reshape(len(ret),1)
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
    with open('tweets.csv','rb') as csvfile:
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

def main(argv):
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
        print(metrics.classification_report(tweet_by_trump_test, predicted,target_names=('Trump','Not Trump')))

if __name__ == "__main__":
    main(sys.argv)


