import language_check as lc
import spacy
from nltk import Tree
from pattern.en import conjugate, lemma, lexeme, INFINITIVE, PRESENT, PAST, PARTICIPLE, FUTURE, SG, PL, INDICATIVE, IMPERATIVE, CONDITIONAL, SUBJUNCTIVE, PROGRESSIVE
import numpy as np # only for writing, reading the master_dictionary

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
			temp.append(ch.lower_ + '_' + ch.tag_)
		if(len(temp) == 2):
			temp.append(payload.lower_+ '_' + ch.tag_)
			if (temp[0][-3:] == 'VBZ' or temp[0][-3:] == 'VBP') and temp[1][-3:] == 'VBN':
				if nounAfterVerb or since:
					x = conjugate(verb=lemma(temp[2][:-4]), tense=PRESENT, mood=INDICATIVE, aspect=PROGRESSIVE, person=1, number=PL)
				elif nounBeforeVerb:
					x = conjugate(verb=lemma(temp[2][:-4]), tense=PAST+PARTICIPLE, mood=INDICATIVE, person=1, number=PL)
				# print(temp[2][:-4] + ' -> ' + x)
			else:
				x = conjugate(verb=lemma(temp[2][:-4]), tense=PRESENT, mood=INDICATIVE, aspect=PROGRESSIVE, person=1, number=PL)
			combos.append(temp)

			raw_text = raw_text[:payload.idx] + raw_text[payload.idx:].replace(temp[2][:-4], x, 1)
			temp = []
			return raw_text
	return raw_text

def VB_IN_NN(payload):
	if(payload.tag_[:2] != 'VB'):
		return
	for ch in payload.children:
		if(ch.tag_[:2] == 'VB'):
			VB_IN_NN(ch)
	temp = [payload]
	for ch in payload.children:
		if(ch.tag_ == "IN"):
			temp.append(ch)
			for sec in ch.children:
				temp.append(sec)
				if(len(temp) == 3):
					grammar[payload.text.lower()] = {}
					grammar[payload.text.lower()][sec.text.lower()] = ch.text.lower()
				return

def VB_IN_NN_correction(payload, raw_text, master_dictionary):
	if(payload.tag_[:2] != 'VB'):
		return
	for ch in payload.children:
		if(ch.tag_[:2] == 'VB'):
			VB_IN_NN_correction(ch, raw_text, master_dictionary)
	temp = [payload]
	for ch in payload.children:
		if(ch.tag_ == "IN"):
			temp.append(ch)
			for sec in ch.children:
				temp.append(sec)
				if(len(temp) == 3):
					try:
						correct_prep = master_dictionary[payload.text.lower()][sec.text.lower()]
						if(correct_prep != ch.text.lower()):
							raw_text = raw_text[:ch.idx] + raw_text[ch.idx:].replace(temp[1].text, correct_prep, 1)
							return raw_text
					except KeyError:
						return raw_text
				return

def modify(text):

	correctly = np.load('./research/correctly.npy').item()

	matches = tool.check(text)
	text = lc.correct(text,matches)
	if(text[-1] != '.'):
		text += '.'

	doc = en_nlp(text)
	for sent in doc.sents:
		text = VB_VB_VB_correction(sent.root, text)
		text = VB_IN_NN_correction(sent.root, text, correctly)

	return text