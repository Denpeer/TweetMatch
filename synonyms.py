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
from collections import defaultdict
import csv


def get_synonyms( synsets, max, ignore, theWord, drank ):
   "function_docstring"
   synl = []
   hyper = []
   hypo = []
   mem_holo = []
   for l in synsets.lemmas():
        if l.name().lower() not in ignore:
            if len(synl) < max:
                if count[l.name()] > 0:
                    #print("synl: "+l.name()+" appears: "+str(count[l.name()]) + " times")
                    synl.append(l.name())
                    ignore.append(l.name().lower())
                    drank[count[l.name()]].append(l.name())
   for h in synsets.hypernyms():
        for l in h.lemmas(): 
            if l.name().lower() not in ignore:
                if len(hyper) < max:
                    if count[l.name()] > 0:
                        #print("hyper: "+l.name()+" appears: "+str(count[l.name()]) + " times")
                        hyper.append(l.name())
                        ignore.append(l.name().lower())
                        drank[count[l.name()]].append(l.name())
                        
   for h in synsets.hyponyms():
        for l in h.lemmas():
            if l.name().lower() not in ignore:
                if len(hypo) < max:
                    if count[l.name()] > 0:
                        #print("hypo: "+l.name()+" appears: "+str(count[l.name()]) + " times")
                        hypo.append(l.name())
                        ignore.append(l.name().lower())
                        drank[count[l.name()]].append(l.name())
   for h in synsets.member_holonyms():
        for l in h.lemmas(): 
            if l.name().lower() not in ignore:
                if len(mem_holo) < max:
                    if count[l.name()] > 0:
                        #print("mem_holo: "+l.name()+" appears: "+str(count[l.name()]) + " times")
                        mem_holo.append(l.name())
                        ignore.append(l.name().lower())
                        drank[count[l.name()]].append(l.name())
   ret_list = []
   if theWord.lower() not in ignore:
       ret_list.append(theWord)
       ignore.append(theWord.lower())
   listoflists = [synl,hyper,hypo,mem_holo]
   for x in listoflists:
       for y in x:
           ret_list.append(y)
   return ret_list

f = open("trump_words.txt","w")
f.truncate

with open('WebServer/App/data/tweets.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        f.write(row['tweet_text'])
    f.close
 
file=open("trump_words.txt","r+")  
 
#tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
tokenizer = RegexpTokenizer(r'\b[^\d\W]+\b')
#tokens = word_tokenize(file.read())
tokens = tokenizer.tokenize(file.read())

file.close()

stop_words = stopwords.words('english')
stop_words.append('co')
stop_words.append('https')
stop_words.append('amp')

tokens = [token for token in tokens if token not in stop_words]    
  
count = Counter(tokens)

example_sent = "Drain the swamp"

word_tokens = word_tokenize(example_sent)

d = defaultdict(list)
kwPos = []
idx = 0
for token in word_tokens:
    if token in stop_words:
        d[idx].append(token)
    else:
        kwPos.append(idx)
    idx = idx + 1

filtered_sentence = []

for w in word_tokens:
    if w not in stop_words:
        filtered_sentence.append(w)

print(word_tokens)
print(filtered_sentence)

swSentence = []
for w in word_tokens:
    swSentence.append([])

for k in d:
    swSentence[k] = d[k][0]
    
print(swSentence)

wordlist = []
ignoreList = []
dfreq= defaultdict(list)
for w in filtered_sentence:
    #print("=> Word: " + w)
    ret = []
    for syn in wordnet.synsets(w):
        for item in get_synonyms(syn, 10, ignoreList, w, dfreq):
            ret.append(item)
    if ret:
        wordlist.append(ret)
    else:
        print("no syn found for word: " + w)
        swSentence[word_tokens.index(w)] = w 

maxGeneratedWords = 10
keylist = sorted(dfreq.keys())
for key in keylist:
    #print ("%s: %s" % (key, dfreq[key]))
    for w in dfreq[key]:
        if w not in word_tokens:
            if sum(len(x) for x in wordlist) > maxGeneratedWords:
                for l in wordlist:
                    if w in l:
                        l.remove(w)
            
  
prod = list(itertools.product(*wordlist))
#print("prod: "+str(prod))

print("***** RESULTS *****")
results = []
for comb in prod:
    i = 0
    temp_res = swSentence
    for w in comb:
        temp_res[kwPos[i]] = w
        i = i + 1
    temp_res = ' '.join(temp_res)
    print(temp_res)
    results.append(temp_res)
