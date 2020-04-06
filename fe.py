import re
import numpy as np
import pandas as pd
import pickle
import gensim
import spacy
import pyLDAvis
import pyLDAvis.gensim
import matplotlib.pyplot as plt
import seaborn as sns
from gensim.utils import simple_preprocess
from gensim import corpora, models
from gensim.parsing.preprocessing import STOPWORDS
from nltk.corpus import stopwords
from gensim.models import CoherenceModel
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
from nltk.tokenize import sent_tokenize
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def replace_words(text):
    text = re.sub(r'U\.S\.', 'US', text)
    text = re.sub(r'U\.S\.A\.', 'US', text)
    text = re.sub(r'US', 'USA', text)
    text = re.sub(r'Kongs', 'Kong', text)
    text = re.sub(r'Hong Kong', 'HongKong', text)
    text = re.sub(r'U\.K\.', 'UK', text)
    text = re.sub(r'Mr\.', 'MR', text)
    text = re.sub(r'Mrs\.', 'MRS', text)
    text = re.sub(r'Ms\.', 'MS', text)
    text = re.sub(r'\.\.\.', '', text)
    text = re.sub(r'U.S-China', 'US-China', text)
    text = text.replace('Co.', 'Co')
    text = text.replace('\xa0', '')
    text = text.replace('."', '".')
    text = text.replace('immediatelywith', 'immediately with')
    text = text.replace('theOfficeof', 'the Office of')
    text = text.replace('theCommissionerof', 'the Commissioner of')
    return text

# Modified from: https://towardsdatascience.com/topic-modeling-and-latent-dirichlet-allocation-in-python-9bf156893c24
def preprocess(text):
    stop_words = stopwords.words('english')
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in stop_words:
            result.append(WordNetLemmatizer().lemmatize(token, pos='v'))
    return ' '.join(result)

def preprocess_all(listy):
    results = [ preprocess(text) for text in listy ]
    return results

# Following functions from https://www.machinelearningplus.com/nlp/topic-modeling-gensim-python/
def make_bigrams(texts):
    bigram = gensim.models.Phrases(data_words, min_count=5, threshold=10)
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    return [ bigram_mod[doc] for doc in texts ]

def make_trigrams(texts):
    trigram = gensim.models.Phrases(bigram[data_words], threshold=10) 
    trigram_mod = gensim.models.phrases.Phraser(trigram)
    return [ trigram_mod[bigram_mod[doc]] for doc in texts ]

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent)) 
        texts_out.append([ token.lemma_ for token in doc if token.pos_ in allowed_postags ])
    return texts_out

def compute_coherence_values(dictionary, corpus, texts, limit, start=2, step=3):
    coherence_values = []
    model_list = []
    for num_topics in range(start, limit, step):
        model = gensim.models.wrappers.LdaMallet(mallet_path,
                                                 corpus=corpus,
                                                 id2word=id2word,
                                                 num_topics=num_topics)
        model_list.append(model)
        coherencemodel = CoherenceModel(model=model,
                                        texts=texts,
                                        dictionary=dictionary,
                                        coherence='c_v')
        coherence_values.append(coherencemodel.get_coherence())

    return model_list, coherence_values
# End taken functions

def vader_analysis(text):
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(text)

def preprocess_all(listy):
    results = [ preprocess(text) for text in listy ]
    return results

def polarity(text):
    analysis = TextBlob(text)
    return analysis.sentiment[0]

def subjectivity(text):
    analysis = TextBlob(text)
    return analysis.sentiment[1]

def topic_sent(sentence_tokens):
    s_tokens = sentence_tokens
    topic_0 = 0
    topic_1 = 0
    topic_2 = 0
    topic_3 = 0
    topic_4 = 0
    topic_5 = 0
    topic_6 = 0
    num_sentences = len(s_tokens)
    for i in range(num_sentences):
        tokens = s_tokens[i].split()
        vec = id2word.doc2bow(tokens)
        # model can be changed
        topic = sorted(tfidf_lda_model[vec], key=lambda tup: tup[1], reverse=True)[0][0]
        sentiment = round(100 * vader_analysis(s_tokens[i])['compound'], 2)
        if topic == 0:
            topic_0 += sentiment / num_sentences
        elif topic == 1:
            topic_1 += sentiment / num_sentences
        elif topic == 2:
            topic_2 += sentiment / num_sentences
        elif topic == 3:
            topic_3 += sentiment / num_sentences
        elif topic == 4:
            topic_4 += sentiment / num_sentences
        elif topic == 5:
            topic_5 += sentiment / num_sentences
        else:
            topic_6 += sentiment / num_sentences
    return (round(topic_0, 2), round(topic_1, 2), round(topic_2, 2), round(topic_3, 2), round(topic_4, 2), round(topic_5, 2), round(topic_6, 2))

