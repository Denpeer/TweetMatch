import csv
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from math import ceil
from sklearn import metrics

# Read tweets from csv
with open('tweets.csv','rb') as csvfile:
    reader = csv.DictReader(csvfile)
    
    # Setup pipeline with countvectorizer, tfidftransformer and stochastic gradient descent Classifier
    text_clf = Pipeline([('vect', CountVectorizer(ngram_range=(1,2))),('tfidf', TfidfTransformer(use_idf=True)),('clf', SGDClassifier(learning_rate='optimal',eta0=0.001,class_weight='balanced',loss='modified_huber', penalty='l2',alpha=1e-3, n_iter=5, random_state=42))])
    
    # Read relevant rows
    tweet_all = [(row['tweet_text'],row['politician_name'],row['tweet_by_trump']) for row in reader]
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
    text_clf = text_clf.fit(tweet_text_train, tweet_by_trump_train)

    # Validate the model
    predicted = text_clf.predict(tweet_text_test)
    #confidence = text_clf.decision_function(tweet_text_test)
    print(metrics.classification_report(tweet_by_trump_test, predicted,target_names=('Trump','Not Trump')))
