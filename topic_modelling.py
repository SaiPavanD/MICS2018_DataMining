from nltk.corpus import stopwords
from nltk.corpus import words
from nltk.stem.wordnet import WordNetLemmatizer
import string

import gensim
from gensim import corpora

import re

from pdfextract import convert_pdf_to_txt_pagewise

class topic_modelling:
    def __init__(self, path):
        self.__journal = [page.decode('utf-8','ignore') for page in convert_pdf_to_txt_pagewise(path)]
        self.__articles = []
        self.__topic_head = []
        self.__ldamodel = None
        self.__doc_term_matrix = []

    def get_article_page_nos(self):
        contents_pages = []
        article_pages = []

        for page_no, page in enumerate(self.__journal):
            for line in page.split('\n'):
                if len(line) < 15:
                    if "contents" in line.lower():
                        contents_pages += [page_no]

        for page_no in contents_pages:
            for line in self.__journal[page_no].split('\n'):
                if len(line) < 8:
                    article_pages += map(int,re.findall(r'\d+', line))

        article_pages = list(set(article_pages))
        article_pages.sort(key = float)
        return article_pages

    def get_page_map(self):
        self.__page_mapping = {}

        for page_no, page in enumerate(self.__journal):
                for line in page.split('\n'):
                    try:
                        actual_page_no = int(line.strip())
                        if actual_page_no not in self.__page_mapping:
                            self.__page_mapping[actual_page_no] = page_no
                        break
                    except:
                        pass

        first_page = min(self.__page_mapping.keys())
        try:
            self.__page_mapping[first_page] = self.__page_mapping[first_page + 1] - 1
        except:
            pass

        return self.__page_mapping

    def seperate_articles(self):
        article_pages = self.get_article_page_nos()
        page_map = self.get_page_map()

        # if contents page is not there, assume each article
        if len(article_pages) == 0:
            article_pages = range(0, len(self.__journal), 10)
        if len(self.__journal) - 1 not in article_pages:
            article_pages += [len(self.__journal) - 1]

        for i in xrange(len(article_pages) - 1):
            begin = article_pages[i]
            end = article_pages[i+1]
            begin_idx = None
            end_idx = None
            self.__topic_head += [str(begin)+'-'+str(end)]

            try:
                begin_idx = page_map[begin]
            except:
                for j in xrange(1,10):
                    if begin + j in page_map:
                        begin_idx = page_map[begin + j] - j
                        break
                if begin_idx is None:
                    for j in xrange(1,10):
                        if begin - j in page_map:
                            begin_idx = page_map[begin - j] + j
                            break
                if begin_idx is None:
                    begin_idx = begin

            try:
                end_idx = page_map[end]
            except:
                for j in xrange(1,10):
                    if end + j in page_map:
                        end_idx = page_map[end + j] - j
                        break
                if begin_idx is None:
                    for j in xrange(1,10):
                        if end - j in page_map:
                            end_idx = page_map[end - j] + j
                            break
                if end_idx is None:
                    end_idx = end

            self.__articles += ['\n'.join(self.__journal[begin_idx:end_idx+1])]

    def clean(self, article):
        stop = set(stopwords.words('english'))
        stop.add(('psychiatry', 'psychiatric', 'mental', 'illness', 'disease', 'lunacy', 'lunatic', 'insane', 'insanity'))
        exclude = set(string.punctuation)
        lemma = WordNetLemmatizer()
        stop_free = ' '.join([i for i in article.lower().split() if i not in stop])
        punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
        normalized = ' '.join(lemma.lemmatize(word) for word in punc_free.split())
        return normalized

    def get_topics(self):
        self.seperate_articles()
        articles_clean = [self.clean(article).split() for article in self.__articles]
        dictionary = corpora.Dictionary(articles_clean)
        self.__doc_term_matrix = [dictionary.doc2bow(article) for article in articles_clean]

        # Creating the object for LDA model using gensim library
        Lda = gensim.models.ldamodel.LdaModel

        # Running and Training LDA model on the document term matrix.
        self.__ldamodel = Lda(self.__doc_term_matrix, num_topics=5, id2word = dictionary, passes=100)

        return self.__ldamodel.print_topics(num_words=20, num_topics=5)

    def get_document_topics(self):
        return zip(self.__topic_head,[self.__ldamodel.get_document_topics(bow) for bow in self.__doc_term_matrix])
