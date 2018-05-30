from topic_modelling import *

a = topic_modelling('./English journal psychiatry/BJP_1902_vol48.pdf')

print a.get_topics()
print a.get_document_topics()
