import language_check as lc
import spacy
from nltk import Tree
from pattern.en import conjugate, lemma, lexeme, INFINITIVE, PRESENT, PAST, PARTICIPLE, FUTURE, SG, PL, INDICATIVE, IMPERATIVE, CONDITIONAL, SUBJUNCTIVE, PROGRESSIVE, singularize
import numpy as np
import os
import time
import tensorflow as tf
from sympound import sympound
import platform

# all the tools required for sentence structure correction
distancefun = None
if platform.system() != "Windows":
	from pyxdameraulevenshtein import damerau_levenshtein_distance
	distancefun = damerau_levenshtein_distance
else:
	from jellyfish import levenshtein_distance
	distancefun = levenshtein_distance
ssc = sympound(distancefun=distancefun, maxDictionaryEditDistance=3)

tool = lc.LanguageTool('en-US')

en_nlp = spacy.load('en')
combos = []

def encode_sentence(english):
	doc = en_nlp(english)
	deps_dict = np.load('./research/deps_dict.npy').item()

	sent_struct = []
	for token in doc:
		try:
			sent_struct.append(deps_dict[token.dep_.lower()])
		except:
			print('no key!')

	sentence_code = ''.join(sent_struct)
	return sentence_code

def decode_coding(code):
	inv_deps_dict = np.load('./research/inv_deps_dict.npy').item()
	code_list = list(code.replace(' ', ''))
	decoded_list = []
	for char in code_list:
		decoded_list.append(inv_deps_dict[char])
	return decoded_list

def VB_VB_VB_correction(payload, raw_text, error_count): # correct errors of type has-been-walking
	if 'been' not in raw_text.split():
		return raw_text, error_count
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
	nounBeforeVerb = False
	nounAfterVerb = False
	verbFound = False
	if(payload.text == 'is' or payload.text == 'was' or payload.text == 'are' or payload.text == 'were'):
		return raw_text, error_count

	for ch in payload.children:
		if(ch.tag_[:2] == 'VB'):
			verbFound = True
		if((not verbFound) and (ch.dep_ == 'nsubj')):
			print(ch.lower_)
			nounBeforeVerb = True
		if(verbFound and (ch.dep_ == 'nsubj')):
			nounAfterVerb = True

		ifHave = False
		ifBeen = False
		if(ch.tag_[:2] == 'VB'): # this might need to be removed
			dummy, error_count = VB_VB_VB_correction(ch, raw_text, error_count)	
			try:
				if(ch.lower_ == 'has') or (ch.lower_ == 'have') or (ch.lower_ == 'had'):
					ifHave = True
				if(ch.lower_ == 'been' or payload.text == "been"):
					ifBeen = True

				if(ifHave and ifBeen):
					x = conjugate(verb=lemma(payload.text), tense=PAST+PARTICIPLE, mood=INDICATIVE, person=1, number=PL)
				elif(nounBeforeVerb and ((ch.lower_ == 'is') or (ch.lower_ == 'are') or (ch.lower_ == 'was') or (ch.lower_ == 'was') or (ch.lower_ == 'were'))):
					x = conjugate(verb=lemma(payload.text), tense=PRESENT, mood=INDICATIVE, aspect=PROGRESSIVE, person=1, number=PL)
				else:
					x = payload.text
				
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

def sentence_correction(payload, sc_dict):
	# optional, only if adding dictionary items is required
	# ssc.create_dictionary_entry("bonjour", 1)
	
	ssc.load_dictionary("./research/sentence_codes.txt", term_index=0, count_index=1)
	payload = encode_sentence(payload)
	print(payload)
	
	if payload in sc_dict:
		print('correct!')
		return 'CORRECT', 'CORRECT'
	
	try:
		# result = ssc.lookup_compound(input_string=payload, edit_distance_max=1) # choose edit_distance carefully
		result = ssc.lookup(input_string=payload, verbosity=0, edit_distance_max=1) # choose edit_distance carefully
	except TypeError:
		print('no matches!')
		return 'NOTFOUND', 'NOTFOUND'
	
	if(result == []):
		return 'NOTFOUND', 'NOTFOUND'
	
	print(result[-1])
	result = str(result[-1]).split(':')
	print('wrong :      ' + payload)
	print('correction : ' + result[0])
	# print('position : ' + result[2])
	
	# ssc.save_pickle("symspell.pickle")
	# ssc.load_pickle("symspell.pickle")

	wrong_sentence_structure = decode_coding(payload)
	correct_sentence_structure = decode_coding(''.join(result[0]))

	return '-'.join(wrong_sentence_structure), '-'.join(correct_sentence_structure)

def modify(text):

	correctly = np.load('./research/correctly.npy').item()
	sentence_codes_dict = np.load('./research/sentence_correction_dict.npy').item()

	vv_errors = 0
	vvv_errors = 0
	prep_errors = 0
	wrong_text_structure = []
	correct_text_structure = []

	matches = tool.check(text)
	text = lc.correct(text,matches)

	doc = en_nlp(text)

	# adding punctuation
	punctFound = False
	for token in doc:
		if(token.dep_ == 'punct'):
			punctFound = True
	if not punctFound:
		text += '.'

	for sent in doc.sents:
		text, e1 = VB_VB_correction(sent.root, text, 0)
		text, e2 = VB_VB_VB_correction(sent.root, text, 0)
		text, e3 = VB_IN_NN_correction(sent.root, text, correctly, 0)
		w, c = sentence_correction(sent.text, sentence_codes_dict)
		wrong_text_structure.append(w)
		correct_text_structure.append(c)
		vv_errors += e1
		vvv_errors += e2
		prep_errors += e3

	errors = [["Spelling errors", len(matches)], ["V-V errors", vv_errors], ["V-V-V errors", vvv_errors], ["Preposition errors", prep_errors], ["Total errors", (len(matches) + vv_errors + vvv_errors + prep_errors)], wrong_text_structure, correct_text_structure]
	return text, errors
