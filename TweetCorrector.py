# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 16:51:31 2017

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

with open('Data/tweets.csv', newline='') as csvfile:
     #spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
     #for row in spamreader:
     #    print('!!! '.join(row))
    reader = csv.DictReader(csvfile)
    name = ""
    
    #create dict to store (autor, tweets) as documents
    d = defaultdict(list)
    
    for row in reader:
        d[row['politician_name']].append(row['tweet_text'])
   
#d = dict((k, tuple(v)) for k, v in d1.items())  

my_analyzer1 = analysis.CommaSeparatedTokenizer() | analysis.LowercaseFilter() | analysis.StopFilter()
my_analyzer2 = analysis.SpaceSeparatedTokenizer() | analysis.LowercaseFilter() | analysis.BiWordFilter()  
ana = analysis.RegexTokenizer() | analysis.BiWordFilter()  
        
schema = fields.Schema(title=fields.TEXT(stored=True), content=fields.TEXT(stored=True), biword=fields.TEXT(analyzer=ana, phrase=False))
ix = create_in("../TestIndex", schema)
writer = ix.writer()
writer.mergetype = writing.CLEAR
for key in d:
    writer.add_document(title=key,  content= ".".join( d[key]), biword=".".join( d[key]))
writer.commit()


# I'll use a SimpleParser here so I don't have to worry about
# what to do with bracketed groups ;)
#qp = qparser.SimpleParser("content", schema=ix.schema, group=qparser.OrGroup)
qp = qparser.QueryParser("content", schema=ix.schema, group=qparser.OrGroup)

qstring = u"the media building"
# Parse the user query
q = qp.parse(qstring)

# Merge the text of adjacent terms
if len(q) > 1:
    text = u" ".join(x.text for x in q if isinstance(x, query.Term))
else:
    text = qstring

pairs = schema["biword"].process_text(text)
biwordq = query.Or([query.Term("biword", pair) for pair in pairs])

# Finally, add the biword query to the original parsed query
q = query.Or([q, biwordq])


# Parse the user query string
#qp = qparser.QueryParser("content", ix.schema)
#q = qp.parse(qstringAna) 

with ix.searcher() as searcher:
    #query = QueryParser("content", ix.schema).parse("third one more")
    corrected = searcher.correct_query(q, qstring)
    if corrected.query != q:
        print("Did you mean:", corrected.string)
    results = searcher.search(q)
    my_sf = highlight.SentenceFragmenter(maxchars=200, sentencechars='.!?', charlimit=None)
    results.fragmenter = my_sf
    print(results[0]['title'])
    print(results[0].highlights("content"))
    #for result in results:
     #   print(result['title'])
      #  print(result.highlights("content"))