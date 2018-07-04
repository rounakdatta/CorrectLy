import os

import os.path

import zipfile

from datetime import datetime

from re import sub



sourceFile = zipfile.ZipFile('DO.docx')



list = sourceFile.namelist()



publicDir = os.getenv("TMP")

timestamp = datetime.now().isoformat()

timestamp = sub("[:.]", "", timestamp)

dirname = "xtemp-jgv-" + timestamp

tempDir = os.path.join(publicDir, dirname)



os.mkdir(tempDir)



sourceFile.extractall(tempDir)



documentPath = os.path.join(tempDir, "word")



document = open(os.path.join(documentPath, "document.xml"), "a+")



document.seek(2666)

print (document.read(466))

print (document.tell())



sourceFile.close()
