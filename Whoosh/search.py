# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 17:26:22 2017

@author: olivierdikken
"""

from whoosh.index import create_in
import whoosh.fields as fields
from whoosh import qparser, query
from whoosh import writing
from whoosh import highlight
from whoosh import analysis
from collections import defaultdict
import csv

with open('../Data/tweets.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    name = ""
    
    #create dict to store (autor, tweets) as documents
    d = defaultdict(list)
    
    for row in reader:
        d[row['politician_name']].append(row['tweet_text']) 

#biword filter analyzer to get more relevant results
ana = analysis.RegexTokenizer() | analysis.BiWordFilter()  
#the schema used only uses title (the author of the tweet) and content (the tweet text). biword is the content filterd by the biwordfilter        
schema = fields.Schema(title=fields.TEXT(stored=True), content=fields.TEXT(stored=True), biword=fields.TEXT(analyzer=ana, phrase=False))
#create local index (TestIndex folder already exists on my computer, one hiearchy level up; this is just for testing since it will be working on the webserver soon) 
ix = create_in("../../TestIndex", schema)

#create the index writer
writer = ix.writer()
#clear the index (useful for testing if we change how the index is build; needs to be removed for speed purposes when done testing)
writer.mergetype = writing.CLEAR
#add all the tweets to a document with as title the author
for key in d:
    writer.add_document(title=key,  content= ".".join( d[key]), biword=".".join( d[key]))
writer.commit()

#create the qparser working on the tweet content using OR instead of AND for the query tokens (because we also use a biword filter)
qp = qparser.QueryParser("content", schema=ix.schema, group=qparser.OrGroup)

#the string to search (test string hardcoded at the moment)
qstring = u"the media building"
# Parse the user query
q = qp.parse(qstring)

# Merge the text of adjacent terms
if len(q) > 1:
    text = u" ".join(x.text for x in q if isinstance(x, query.Term))
else:
    text = qstring

#apply the biword filter to the joined tokens of the query
pairs = schema["biword"].process_text(text)
#create the biword query as an OR set of biword pairs
biwordq = query.Or([query.Term("biword", pair) for pair in pairs])

# Finally, add the biword query to the original parsed query
q = query.Or([q, biwordq])

with ix.searcher() as searcher:
    corrected = searcher.correct_query(q, qstring)
    #spelling suggestion
    if corrected.query != q:
        print("Did you mean:", corrected.string)
    #the search results
    results = searcher.search(q)
    #use a sentence fragmenter since this is not a normal search engine and we want the full sentences to be returned
    my_sf = highlight.SentenceFragmenter(maxchars=200, sentencechars='.!?', charlimit=None)
    results.fragmenter = my_sf
    #show the first result title (politician name) and highlight the matched words in the result
    print(results[0]['title'])
    print(results[0].highlights("content"))