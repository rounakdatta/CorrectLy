from docx import Document

def scrape_docx(docx):
    raw_doc = Document(docx)
    parsed_text = ""
    for para in raw_doc.paragraphs:
    	parsed_text += (para.text + "\n")

    return parsed_text