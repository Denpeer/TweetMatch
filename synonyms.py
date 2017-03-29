# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 10:34:45 2017

@author: olivierdikken
"""
import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from collections import Counter
import itertools
import csv


f = open("trump_words.txt","w")
f.truncate

with open('Data/tweets.csv', newline='') as csvfile:
     #spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
     #for row in spamreader:
     #    print('!!! '.join(row))
    reader = csv.DictReader(csvfile)
    
    for row in reader:
        f.write(row['tweet_text'])
    f.close
 
file=open("trump_words.txt","r+")  
 
#tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
tokenizer = RegexpTokenizer(r'\b[^\d\W]+\b')
#tokens = word_tokenize(file.read())
tokens = tokenizer.tokenize(file.read())


stop_words = stopwords.words('english')
stop_words.append('co')
stop_words.append('https')
stop_words.append('amp')

tokens = [token for token in tokens if token not in stop_words]
  
count = Counter(tokens)

  
wordcount={}
for word in file.read().split():
    if word not in wordcount:
        wordcount[word] = 1
    else:
        wordcount[word] += 1



example_sent = "America is good once again"

word_tokens = word_tokenize(example_sent)

filtered_sentence = []

for w in word_tokens:
    if w not in stop_words:
        filtered_sentence.append(w)

print(word_tokens)
print(filtered_sentence)

wordlist = []

for w in filtered_sentence:
    print("=> Word: " + w)
    synlist = []
    for syn in wordnet.synsets(w):
        for l in syn.lemmas():
            if l.name() not in synlist:
                if len(synlist) < 10:
                    if count[l.name()] > 1:
                        print(l.name()+" appears: "+str(count[l.name()]) + " times")
                        synlist.append(l.name())
    wordlist.append(synlist)
    
for w in filtered_sentence:
    print("=> Word: " + w)
    for syn in wordnet.synsets(w):
        wordlist.append(get_synonyms(syn, 10))

    

    
prod = list(itertools.product(*wordlist))
#print(prod)




def get_synonyms( synsets, max ):
   "function_docstring"
   hyper = []
   hypo = []
   mem_holo = []
   root_hyper = []
   for h in syn.hypernyms():
        for l in h.lemmas(): 
            if l.name() not in synlist:
                if len(synlist) < max:
                    if count[l.name()] > 1:
                        print(l.name()+" appears: "+str(count[l.name()]) + " times")
                        synlist.append(l.name())
    for h in syn.hyponyms():
        for l in h.lemmas():
            if l.name() not in synlist:
                if len(synlist) < max:
                    if count[l.name()] > 1:
                        print(l.name()+" appears: "+str(count[l.name()]) + " times")
                        synlist.append(l.name())
    for h in syn.member_holonyms():
        for l in h.lemmas(): 
            if l.name() not in synlist:
                if len(synlist) < max:
                    if count[l.name()] > 1:
                        print(l.name()+" appears: "+str(count[l.name()]) + " times")
                        synlist.append(l.name())
    for h in syn.root_hypernyms():
        for l in h.lemmas(): 
            if l.name() not in synlist:
                if len(synlist) < max:
                    if count[l.name()] > 1:
                        print(l.name()+" appears: "+str(count[l.name()]) + " times")
                        synlist.append(l.name())
        ret_list = []
        listoflists = [hyper,hypo,mom_holo,root_hyper]
        for x in listoflists:
            for y in x:
                ret_list.append(y)
   return ret_list