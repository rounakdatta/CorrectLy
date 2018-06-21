import language_check as lc
import spacy
from nltk import Tree
from pattern.en import conjugate, lemma, lexeme, INFINITIVE, PRESENT, PAST, PARTICIPLE, FUTURE, SG, PL, INDICATIVE, IMPERATIVE, CONDITIONAL, SUBJUNCTIVE, PROGRESSIVE
import numpy as np # only for writing, reading the master_dictionary

tool = lc.LanguageTool('en-US')

en_nlp = spacy.load('en')
combos = []

def VB_VB_VB_correction(payload, raw_text, error_count): # correct errors of type has-been-walking
	if(payload.tag_[:2] != 'VB' and payload.tag_[:2] != 'NN'  and payload.tag_[:2] != 'JJ'):
		return raw_text, error_count
	for ch in payload.children:
		if(ch.tag_[:2] == 'VB'): # this might need to be removed
			dummy, error_count = VB_VB_VB_correction(ch, raw_text, error_count)
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
			try:
				if (temp[0][-3:] == 'VBZ' or temp[0][-3:] == 'VBP') and temp[1][-3:] == 'VBN':
					if nounAfterVerb or since:
						x = conjugate(verb=lemma(temp[2][:-4]), tense=PRESENT, mood=INDICATIVE, aspect=PROGRESSIVE, person=1, number=PL)
					elif nounBeforeVerb:
						x = conjugate(verb=lemma(temp[2][:-4]), tense=PAST+PARTICIPLE, mood=INDICATIVE, person=1, number=PL)
					# print(temp[2][:-4] + ' -> ' + x)
				else:
					x = conjugate(verb=lemma(temp[2][:-4]), tense=PRESENT, mood=INDICATIVE, aspect=PROGRESSIVE, person=1, number=PL)
				combos.append(temp)

				if(x != temp[2][:-4]):
					error_count += 1
				raw_text = raw_text[:payload.idx] + raw_text[payload.idx:].replace(temp[2][:-4], x, 1)
				temp = []
				return raw_text, error_count
			except TypeError:
				return raw_text, error_count
	return raw_text, error_count

def VB_VB_correction(payload, raw_text, error_count): # correct errors of type is-walking OR has-cooked
	if(payload.tag_[:2] != 'VB'):
		return raw_text, error_count
	for ch in payload.children:
		if(ch.tag_[:2] == 'VB'): # this might need to be removed
			dummy, error_count = VB_VB_VB_correction(ch, raw_text, error_count)	
			try:
				if(ch.lower_ == 'has') or (ch.lower_ == 'have') or (ch.lower_ == 'had'):
					x = conjugate(verb=lemma(payload.text), tense=PAST+PARTICIPLE, mood=INDICATIVE, person=1, number=PL)
				else:
					x = conjugate(verb=lemma(payload.text), tense=PRESENT, mood=INDICATIVE, aspect=PROGRESSIVE, person=1, number=PL)
				
				if(x != payload.text):
					error_count += 1
				raw_text = raw_text[:payload.idx] + raw_text[payload.idx:].replace(payload.text, x, 1)
				return raw_text, error_count
			except TypeError:
				return raw_text, error_count
	return raw_text, error_count

def VB_IN_NN(payload): # generate verb-preposition-noun combos (IN is a misnomer here)
	if(payload.tag_[:2] != 'VB'):
		return raw_text
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

def VB_IN_NN_correction(payload, raw_text, master_dictionary, error_count): # correct the verb-preposition-noun combos from the master dict
	if(payload.tag_[:2] != 'VB'):
		return raw_text, error_count
	for ch in payload.children:
		if(ch.tag_[:2] == 'VB'):
			dummy, error_count = VB_IN_NN_correction(ch, raw_text, master_dictionary, error_count)
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
							error_count += 1
							raw_text = raw_text[:ch.idx] + raw_text[ch.idx:].replace(temp[1].text, correct_prep, 1)
							return raw_text, error_count
					except KeyError:
						return raw_text, error_count
	return raw_text, error_count

def modify(text):

	correctly = np.load('./research/correctly.npy').item()

	vv_errors = 0
	vvv_errors = 0
	prep_errors = 0

	matches = tool.check(text)
	text = lc.correct(text,matches)
	if(text[-1] != '.'):
		text += '.'

	doc = en_nlp(text)
	for sent in doc.sents:
		text, e1 = VB_VB_correction(sent.root, text, 0)
		text, e2 = VB_VB_VB_correction(sent.root, text, 0)
		text, e3 = VB_IN_NN_correction(sent.root, text, correctly, 0)
		vv_errors += e1
		vvv_errors += e2
		prep_errors += e3

	errors = [["Spelling errors", len(matches)], ["V-V errors", vv_errors], ["V-V-V errors", vvv_errors], ["Preposition errors", prep_errors], ["Total errors", (len(matches) + vv_errors + vvv_errors + prep_errors)]]
	return text, errors