# CorrectLy - The English text corrector

CorrectLy is an NLP-based spelling and grammar correction tool that accepts articles as well as raw text and returns a corrected sentence. This automated proof-reading tool can correct incorrect words, correct verb-forms based on the sentence tense, correct preposition-noun agreements as well as suggest correct sentence structure. CorrectLy is built using Python, powered by data and makes use of core NLP techniques.

## NLP

The project makes extensive use of the following Python NLP libraries:
 - **SpaCy** (excellent library for splitting into sentences, tokenizing sentence, generating POS tags and determiners)
 - **NLTK** (helps in tokenizing, visualizing sentence structure tree, has huge collection of data corpus)
 - **language_check** (great spelling-correction library with extensive support for simple grammar suggestions, punctuation errors)
 - **pattern** (a CLiPS product which helps in conjugating verbs - helps form the correct structure of the verb based on the tense, person, number, mood)
 - **sympound** (another spelling correction algorithm-based library which even accepts dictionary)
 - **numpy** (for minor mathematical calculations and memory-storage of dictionaries)

## Algorithms

Grammar correction algorithms are implemented with help from these libraries. There are algorithms for:

 - Spelling correction (what are yuo doign in hte collrge -> **What are you doing in the college.**)
  V-V correction (He is play in the garden. -> **He is playing in the garden.**)
 - V-V-V correction (Harry has been watched movie since afternoon. -> **Harry has been watching movie since afternoon.**)
 - Preposition correction (The children are sitting on the room. -> **The children are sitting in the room.**)
 - Sentence structure correction (I am looking at boy. -> **I am looking at the boy.**)

## Getting started

The project has been built entirely using Python 3. The backend framework is powered by Flask. To install all the dependencies, you need to clone the repository, navigate to it and  type ``make install``. To start the application, you can type ``make start`` OR ``python3 app.py`` and then navigate to [localhost:5000](http://localhost:5000).

The application can be used as:

 1. Raw text inputted through the text box.
 2. DocX document uploaded and processed with all text formatting taken care of. The spelling and grammar-corrected document is returned in the DocX format.

The application outputs the corrected document / raw text with some statistics:

 - Number of errors of each type
 - Total number of errors (indicates the severity of the document)
 - Display the table containing the incorrect sentence structure and the correct sentence structure.

## To Do

 - [ ] The preposition as well as sentence structure correction is powered by data - so more the data, better it works. So, **dataset improvement**.
 - [ ] The system still isn't very natural in suggesting the sentences (and might break for extreme cases) - so replacing the algorithms with a **neural network-integrated approach**.
