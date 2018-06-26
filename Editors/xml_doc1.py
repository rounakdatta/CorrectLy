import zipfile
from lxml import etree

zip = zipfile.ZipFile('DO.docx')
xml_content = zip.read('word/document.xml')
print(xml_content)
pedh=etree.fromstring(xml_content)
#print(pedh)

def _itertext(my_etree):
     """Iterator to go through xml tree's text nodes"""
     for node in my_etree.iter(tag=etree.Element):
         if _check_element_is(node, 't'):
             yield (node, node.text)

def _check_element_is(element, type_char):
     word_schema = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
     return element.tag == '{%s}%s' % (word_schema,type_char)

for node, txt in _itertext(pedh):
    print (txt)
