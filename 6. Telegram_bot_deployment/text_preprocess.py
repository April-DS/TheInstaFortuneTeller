import re
import gensim, spacy
from gensim.utils import lemmatize, simple_preprocess
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use', 'not', 'lot', 'lack', 'one',
                   '_', 'be', 'done', 'rather', 'much', 'know','make',
                  've','us','will','com', 'last', 'also', 'go', 'make', 'much', 'see'])
# import regression

# Take caption text from regression (first function)
# preprocess text from caption
# return list of words (from caption)

# predict_range, predict_likes, predict_engagement, caption_text = regression.like_predictor()

# Text preprocessing
def process_words(caption_text, stop_words=stop_words, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """Remove Stopwords and Lemmatization"""
    # predict_range, predict_likes, predict_engagement, caption_text = regression.like_predictor()
    # print(predict_range, predict_likes, predict_engagement)

    caption_text = re.sub("[^a-zA-Z]", " ", caption_text)
    tokenizer = RegexpTokenizer(r'\w+')
    caption_text = tokenizer.tokenize(caption_text.lower())
    text = [simple_preprocess(doc) for doc in caption_text if doc not in stop_words]
    text_out = []
    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
    doc = nlp(" ".join(word[0] for word in text if len(word) >0))
    text_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    # remove stopwords once more after lemmatization
    text_out = [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in text_out]
    return text_out[0]

# process_words(caption_text)