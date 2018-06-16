import language_check as lc
import spacy
from nltk import Tree
from pattern.en import conjugate, lemma, lexeme, INFINITIVE, PRESENT, PAST, PARTICIPLE, FUTURE, SG, PL, INDICATIVE, IMPERATIVE, CONDITIONAL, SUBJUNCTIVE, PROGRESSIVE

tool = lc.LanguageTool('en-US')

en_nlp = spacy.load('en')
combos = []

def VB_VB_VB_correction(payload, raw_text):
    if(payload.tag_[:2] != 'VB' and payload.tag_[:2] != 'NN'  and payload.tag_[:2] != 'JJ'):
        return
    for ch in payload.children:
        if(ch.tag_[:2] == 'VB'): # this might need to be removed
            VB_VB_VB_correction(ch, raw_text)
    temp = []
    nounBeforeVerb = False
    nounAfterVerb = False
    verbFound = False
    since = False
    for ch in payload.children:
        if(ch.tag_[:2] == 'VB'):
            verbFound = True
        if((not verbFound) and (ch.tag_[:2] == 'NN' or ch.tag_[:2] == 'PR')):
            nounBeforeVerb = True
        if(verbFound and (ch.tag_[:2] == 'NN' or ch.tag_[:2] == 'PR')):
            nounAfterVerb = True
        if(ch.lower_ == 'since'):
            since = True
    for ch in payload.children:
        if(ch.tag_[:2] == 'VB'):
            # print(ch.idx)
            temp.append(ch.lower_ + '_' + ch.tag_)
        if(len(temp) == 2):
            temp.append(payload.lower_+ '_' + ch.tag_)
            #print(temp)
            if (temp[0][-3:] == 'VBZ' or temp[0][-3:] == 'VBP') and temp[1][-3:] == 'VBN':
                if nounAfterVerb or since:
                    x = conjugate(verb=lemma(temp[2][:-4]), tense=PRESENT, mood=INDICATIVE, aspect=PROGRESSIVE, person=1, number=PL)
                elif nounBeforeVerb:
                    x = conjugate(verb=lemma(temp[2][:-4]), tense=PAST+PARTICIPLE, mood=INDICATIVE, person=1, number=PL)
                # print(temp[2][:-4] + ' -> ' + x)
            combos.append(temp)
            # print(nounBeforeVerb)
            raw_text = raw_text[:payload.idx] + raw_text[payload.idx:].replace(temp[2][:-4], x, 1)
            #print(raw_text)
            temp = []
            return raw_text
    return raw_text

def modify(text):

	matches = tool.check(text)
	text = lc.correct(text,matches)
	if(text[-1] != '.'):
		text += '.'

	doc = en_nlp(text)
	for sent in doc.sents:
		text = VB_VB_VB_correction(sent.root, text)

	return text