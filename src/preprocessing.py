import string
import nltk
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords
import spacy

# Loading the spacy model once
nlp = spacy.load('en_core_web_sm')

# Loading the stop words once
stop_words = set(stopwords.words('english'))

def load_document(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
    
def clean_text(text):
    # lowercasing
    text = text.lower()
    # Removing punctuation
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    return text

def tokenize(text):
    return text.split()
    
def remove_stopwords(tokens):
    return [token for token in tokens if token not in stop_words]

def lemmatize_tokens(tokens):
    doc = nlp(' '.join(tokens))
    return [token.lemma_ for token in doc]

def rejoin_tokens(tokens):
    return ' '.join(tokens)

def preprocess_text(text):
    cleaned_text = clean_text(text)
    tokens = tokenize(cleaned_text)
    tokens_no_stopwords = remove_stopwords(tokens)
    lemmatized_tokens = lemmatize_tokens(tokens_no_stopwords)
    final_text = rejoin_tokens(lemmatized_tokens)
    return final_text

def preprocess_document(file_path):
    text = load_document(file_path)
    return preprocess_text(text)