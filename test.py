from topic_modelling import topic_modelling

a = topic_modelling('./English journal psychiatry/BJP 1862k1863_vol8_nr44-ocr.pdf')

print a.get_topics()
print a.get_document_topics()
