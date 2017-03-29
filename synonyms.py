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
import os.path
import csv


def get_synonyms( synsets, max, ignore, theWord, drank, count ):
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


def write_tweets_to_file(path):
    if not path:
        trump_text_file_path = "trump_words.txt"
    else:
        trump_text_file_path = path
    
    f = open(trump_text_file_path,"w+")
    f.truncate

    with open('Data/tweets.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            f.write(row['tweet_text'])
        f.close
 
 
def tokenize_file(path):
    if not path:
        trump_text_file_path = "trump_words.txt"
    else:
        trump_text_file_path = path
    file=open(trump_text_file_path,"r+")  
 
    #tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    tokenizer = RegexpTokenizer(r'\b[^\d\W]+\b')
    #tokens = word_tokenize(file.read())
    tokens = tokenizer.tokenize(file.read())
    
    file.close()
    return tokens

def setup_stopwords(ls):
    stop_words = stopwords.words('english')
    stop_words.append('co')
    stop_words.append('https')
    stop_words.append('amp')
    if ls:
        for w in ls:
            stop_words.append(w)
    return stop_words


def log_wordpos(word_tokens, stop_words):    
    d = defaultdict(list)
    kwPos = []
    idx = 0
    for token in word_tokens:
        if token in stop_words:
            d[idx].append(token)
        else:
            kwPos.append(idx)
        idx = idx + 1
    return d, kwPos


def rm_stopwords(word_tokens, stop_words, d):
    filtered_sentence = []
    
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)
    
    swSentence = []
    #make empty placeholders for the words
    for w in word_tokens:
        swSentence.append([])
    #add the stop words to the swSentence
    for k in d:
        swSentence[k] = d[k][0]
    return filtered_sentence, swSentence

def build_wordlist(filtered_sentence, word_tokens, swSentence, count):
    wordlist = []
    ignoreList = []
    #frequency of keywords
    dfreq= defaultdict(list)
    for w in filtered_sentence:
        ret = []
        for syn in wordnet.synsets(w):
            for item in get_synonyms(syn, 10, ignoreList, w, dfreq, count):
                ret.append(item)
        if ret:
            wordlist.append(ret)
        else:
            swSentence[word_tokens.index(w)] = w
    return wordlist, dfreq

def shrink_wordlist(wordlist, word_tokens, dfreq, maxGeneratedWords):
    keylist = sorted(dfreq.keys())
    for key in keylist:
        #print ("%s: %s" % (key, dfreq[key]))
        for w in dfreq[key]:
            if w not in word_tokens:
                if sum(len(x) for x in wordlist) > maxGeneratedWords:
                    for l in wordlist:
                        if w in l:
                            l.remove(w)
    return wordlist
            

def generate_new_queries(wordlist, kwPos, swSentence):
    prod = list(itertools.product(*wordlist))
    results = []
    for comb in prod:
        i = 0
        temp_res = swSentence
        for w in comb:
            temp_res[kwPos[i]] = w
            i = i + 1
        temp_res = ' '.join(temp_res)
        results.append(temp_res)
    return results
    
    
def main(argv):
    path = "trump_words.txt"
    maxGeneratedWords = 10
    write_tweets_to_file(path)
    
    stop_words = setup_stopwords([])
    all_tokens = tokenize_file(path)
    all_tokens = [token for token in all_tokens if token not in stop_words]    
      
    count = Counter(all_tokens)
    
    example_sent = "Drain the swamp"
    
    word_tokens = word_tokenize(example_sent)
    
    d, kwPos = log_wordpos(word_tokens, stop_words)
    filtered_sentence, swSentence = rm_stopwords(word_tokens, stop_words, d)
    wordlist, dfreq = build_wordlist(filtered_sentence, word_tokens, swSentence, count)
    wordlist = shrink_wordlist(wordlist, word_tokens, dfreq, maxGeneratedWords)
    new_queries = generate_new_queries(wordlist, kwPos, swSentence)
    print(new_queries)
   

if __name__ == "__main__":
    main(sys.argv)
