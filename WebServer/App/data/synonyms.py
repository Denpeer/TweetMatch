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
import os
import csv
from App.data.sgd import predict, checkData


#use nltk synsets to get synonyms, hypernyms, hyponums and member holonyms
#max limits the max of each type of synonym, drank is a dict with (appearances, word) based on trump's tweets
#ignore is the list of words that have already been added to the list but can also be used to ignore certain words if hardcoded
def get_synonyms( synsets, max, ignore, theWord, drank, count ):
   "function_docstring"
   #init the data structs
   synl = []
   hyper = []
   hypo = []
   mem_holo = []
   #get synonyms
   for l in synsets.lemmas():
        if l.name().lower() not in ignore:
            if len(synl) < max:
                if count[l.name()] > 0:
                    synl.append(l.name())
                    ignore.append(l.name().lower())
                    drank[count[l.name()]].append(l.name())
   #get hypernyms 
   for h in synsets.hypernyms():
        for l in h.lemmas(): 
            if l.name().lower() not in ignore:
                if len(hyper) < max:
                    if count[l.name()] > 0:
                        hyper.append(l.name())
                        ignore.append(l.name().lower())
                        drank[count[l.name()]].append(l.name())
   #get hyponyms                     
   for h in synsets.hyponyms():
        for l in h.lemmas():
            if l.name().lower() not in ignore:
                if len(hypo) < max:
                    if count[l.name()] > 0:
                        hypo.append(l.name())
                        ignore.append(l.name().lower())
                        drank[count[l.name()]].append(l.name())
   #get member holonyms
   for h in synsets.member_holonyms():
        for l in h.lemmas(): 
            if l.name().lower() not in ignore:
                if len(mem_holo) < max:
                    if count[l.name()] > 0:
                        mem_holo.append(l.name())
                        ignore.append(l.name().lower())
                        drank[count[l.name()]].append(l.name())
   #init the list to be returned
   ret_list = []
   if theWord.lower() not in ignore:
       ret_list.append(theWord)
       ignore.append(theWord.lower())
   listoflists = [synl,hyper,hypo,mem_holo]
   #add the found words to the ret_list
   for x in listoflists:
       for y in x:
           ret_list.append(y)
   return ret_list

#writes all tweets of donald trump to a text file to use for word frequency
def write_tweets_to_file(path):
    if not path:
        trump_text_file_path = "trump_words.txt"
    else:
        trump_text_file_path = path
    
    f = open(trump_text_file_path,"w+")
    f.truncate

    with open('tweets.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['politician_name'] == 'Donald J. Trump':
                f.write(row['tweet_text'])
        f.close
 
#tokenzie all words of the text file containing trump's tweets
def tokenize_file(path):
    if not path:
        trump_text_file_path = "trump_words.txt"
    else:
        trump_text_file_path = path
    file=open(trump_text_file_path,"r+")  
 
    #remove words containing digits and punctuation
    tokenizer = RegexpTokenizer(r'\b[^\d\W]+\b')
    tokens = tokenizer.tokenize(file.read())
    
    file.close()
    return tokens

#init list of stop words
def setup_stopwords(ls):
    stop_words = stopwords.words('english')
    #most recurring words that are not words from trumps tweets
    stop_words.append('co')
    stop_words.append('https')
    stop_words.append('amp')
    if ls:
        for w in ls:
            stop_words.append(w)
    return stop_words

#log the positions of stop words and keywords to build the queries later
def log_wordpos(word_tokens, stop_words):    
    d = defaultdict(list)
    kwPos = []
    idx = 0
    #fill a dict with the stop word positions and the words
    for token in word_tokens:
        if token in stop_words:
            d[idx].append(token)
        else:
            #save keyword positions
            kwPos.append(idx)
        idx = idx + 1
    return d, kwPos

#remove stopwords from the query
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

#using the filtered sentence, set of word tokens (the tokenized user query), the stop word sentence and the term frequency count
#build a list of similar words and their frequency
def build_wordlist(filtered_sentence, word_tokens, swSentence, count):
    wordlist = []
    ignoreList = []
    #frequency of keywords
    dfreq= defaultdict(list)
    for w in filtered_sentence:
        ret = []
        #if spelling mistake or wierd word then no synonyms but still keep word
        if not wordnet.synsets(w):
            ret.append(w)
        for syn in wordnet.synsets(w):
            for item in get_synonyms(syn, 10, ignoreList, w, dfreq, count):
                ret.append(item)
        if ret:
            wordlist.append(ret)
        else:
            swSentence[word_tokens.index(w)] = w
    return wordlist, dfreq

#remove words that do not appear often in trump's tweets
def shrink_wordlist(wordlist, word_tokens, dfreq, maxGeneratedWords):
    keylist = sorted(dfreq.keys())
    for key in keylist:
        for w in dfreq[key]:
            if w not in word_tokens:
                if sum(len(x) for x in wordlist) > maxGeneratedWords:
                    for l in wordlist:
                        if w in l:
                            l.remove(w)
    return wordlist
            
#combine similar word results to generate a list of similar queries that might be more similar to trump's tweets
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
    
#input: a tweet/query, prints a list of similar queries that might be more trump-like   
def main(argv):
    checkData("tweets.csv"," ")
    if not argv:
        #test string in case of empty input
        new_queries = expand_query("Build schools to educate the people of US", 10)
    else:
        new_queries = expand_query(argv, 10)
    
    get_prediction_results(new_queries,"dumped_classifier.pkl")
    
    
def expand_query(query, maxWords):
    path = "trump_words.txt"
    if os.path.isfile(path):
        statinfo = os.stat(path)
        if statinfo.st_size == 0:
            write_tweets_to_file(path)
    else:
        write_tweets_to_file(path)
    #init stop words list
    stop_words = setup_stopwords([])
    #tokenize trump's tweets
    all_tokens = tokenize_file(path)
    #rm stop words
    all_tokens = [token for token in all_tokens if token not in stop_words]    
    #count trump's term frequency
    count = Counter(all_tokens)    
    #tokenize the query
    word_tokens = word_tokenize(query)   
    #log stop word and keyword positions
    d, kwPos = log_wordpos(word_tokens, stop_words)
    #filter the query from stopwords
    filtered_sentence, swSentence = rm_stopwords(word_tokens, stop_words, d)
    #generate a list of similar words
    wordlist, dfreq = build_wordlist(filtered_sentence, word_tokens, swSentence, count)
    #shrink list of similar words for efficiency
    wordlist = shrink_wordlist(wordlist, word_tokens, dfreq, maxWords)
    #generate list of new queries that might be more similar to what trump tweets
    new_queries = generate_new_queries(wordlist, kwPos, swSentence)
    #print the resulting string list
    return new_queries
 
   
def get_prediction_results(qls, pickleFile):
    predlist = []
    for q in qls:
        predlist.append(predict(q,pickleFile))

    scores = defaultdict(list)
    i = 0
    if predlist:
        for pred in predlist:
            scores[pred[2]] = qls[i]
            i = i + 1
        keylist = list(reversed(sorted(scores.keys())))
        print("Most trump like suggestion: "+scores[keylist[0]])
    else:
        print("No suggestions found")
        
    return scores, keylist
    
def get_suggestions(query, pickleFile):
    new_queries = expand_query(query, 10)
    return get_prediction_results(new_queries, pickleFile)

if __name__ == "__main__":
    main("I would like to construct a wall around the usa")