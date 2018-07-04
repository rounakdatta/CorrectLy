from docx import Document
from textblob import TextBlob

para_c = 0
sent_p_c = []
ts = 0

def scrape_docx(docx):
    global para_c, ts
    para_c = 0
    sent_p_c = []
    raw_doc = Document(docx)
    parsed_text = ""
    for para in raw_doc.paragraphs:
        sent_c = 0
        para_c = para_c + 1
        parsed_text += (para.text + "\n")
        t = TextBlob(para.text)
        for sen in t.sentences:
            sent_c = sent_c + 1
            ts = ts + 1
        sent_p_c.append(sent_c)
    print(para_c)
    print(sent_c)
    
    print(sent_p_c)
    return parsed_text, para_c, sent_c, sent_p_c, ts
