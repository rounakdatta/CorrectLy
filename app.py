import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import glob
from uuid import uuid4
import subprocess
from textblob import TextBlob
import docx
from src import checker
from src.extractdoc import scrape_docx

UPLOAD_FOLDER = './test'
ALLOWED_EXTENSIONS = set(['docx'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def serve():
    return render_template("index.html")


@app.route('/file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            print('no filename')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            text, para_c, sent_c, sent_p_c, total = scrape_docx('./test/' + filename)

            corrected, errors = checker.modify(text)
            sent=[]
            t=TextBlob(corrected)
            for sen in t.sentences:
                sent.append(str(sen))

            doc1 = docx.Document()
            print(sent)
            ts = 0

            for p in range(para_c):
                para = ""
                for s in range(sent_p_c[p]):
                    if(ts < total):
                        print(ts)
                        para = para + sent[ts] + " "
                        ts = ts + 1
                a = doc1.add_paragraph(para)
            doc1.save('RESULT.docx')

            return render_template('index.html', correct=corrected, wrong=text, errors=errors)

    return render_template('index.html')

@app.route('/text', methods=['GET', 'POST'])
def upload_text():
    if request.method == 'POST' and 'textupload' in request.form:
        text = request.form['textupload']
        corrected, errors = checker.modify(text)

        return render_template('index.html', correct=corrected, wrong=text, errors=errors)

    return render_template('index.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)