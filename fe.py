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

