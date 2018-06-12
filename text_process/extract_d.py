import docx2txt

def scrape_docx(docx):

    text = docx2txt.process(docx)

    return text

