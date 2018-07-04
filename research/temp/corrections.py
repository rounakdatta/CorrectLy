# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 00:31:38 2018

@author: Saurav
"""
import language_check
from textblob import TextBlob,Word
import re

tool = language_check.LanguageTool('en-US')

s_mistakes=0

q1=["if","should"]
q=["are","who","who's","will","which","what","when","why","how","has","would","have"]

def mistake_checker(sent):
    s=sent.words
    global s_mistakes
    for i in s:
        word=i.correct()
        if(i!=word):
            #print("check",i,word)
            s_mistakes=s_mistakes+1
    #print(mistakes)

def count_inc():
    global s_mistakes
    #print("x")
    #print(mistakes)
    return s_mistakes    

def question(s,l):
    wc=0
    for i in q:
        if(re.search(i,s[0],re.IGNORECASE)):
            wc=1
    if(wc==1):        
        return (1,s)
    else:
        return (0,s)

def correct(sent):
    mistake_checker(sent)
    sent=sent.correct()
    s=sent.split(" ")
    l=len(s)
    n,s=question(s,l-1)
    #print("n",n)
    sent=" ".join(str(x) for x in s)
    #print(type(sent))
    t="?"
    #print("?",type(t))
    if(n==1):
        
        sent=sent+t
    
    matches = tool.check(sent)
    sent=language_check.correct(sent,matches)
    print(sent)

    return sent
    
