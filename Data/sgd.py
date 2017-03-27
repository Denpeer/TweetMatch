import sys
import csv
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from math import ceil
from sklearn import metrics

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


def train(X,Y):
    # Setup pipeline with countvectorizer, tfidftransformer and stochastic gradient descent Classifier
    text_clf = Pipeline([('vect', CountVectorizer(ngram_range=(1,2))),('tfidf', TfidfTransformer(use_idf=True)),('clf', SGDClassifier(learning_rate='optimal',eta0=0.001,class_weight='balanced',loss='modified_huber', penalty='l2',alpha=1e-3, n_iter=5, random_state=42))])

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


