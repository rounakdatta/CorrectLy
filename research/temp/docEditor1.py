import docx
from textblob import TextBlob
from corrections import *
import language_check
import spacy

doc=docx.Document("DO.docx")
paras=doc.paragraphs
l=len(paras)
    
#print(l)
#print(p[0].text)
#print(type(l))

'''
for i in range (len(p)):
    for j in range (len(p[i].runs)):
        print("j",j)
        print(p[i].runs[j].text)
        #print("--------------------------------")
        #print(p[i].style)
        #p[i].style='Normal'
        #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        #print(p[i].runs[j].style)
        #print("--------------------------------")
    print("############################")
    print("i",i)
'''

nlp=spacy.load('en_core_web_sm')

for i in range (len(paras)):
    #print(p[i].text)
    
    t=nlp(paras[i].text)
    for sent in t.sents:
        print(sent.text)
    #t=TextBlob(paras[i].text)
    #for sen in t.sentences:
        #print(sen)
        correct(sent)
        #print("------------------------------------------------")
    
doc.save('mod.docx')
#doc.save('DO.docx')

    
    
