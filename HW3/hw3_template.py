#%%
import numpy as np
import pandas as pd
import nltk
import sklearn 
import string
import re # helps you filter urls

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')    # Use nltk downloader to download resource "punkt" once
nltk.download('punkt_tab')    # Use nltk downloader to download resource "punkt_tab" once

from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from collections import Counter
from nltk.tokenize import word_tokenize # type: ignore
from sklearn.model_selection import KFold

#%%
#Whether to test your Q9 for not? Depends on correctness of all modules
def test_pipeline():
    return False # Make this true when all tests pass

# Convert part of speech tag from nltk.pos_tag to word net compatible format
# Simple mapping based on first letter of return tag to make grading consistent
# Everything else will be considered noun 'n'
posMapping = {
# "First_Letter by nltk.pos_tag":"POS_for_lemmatizer"
    "N":'n',
    "V":'v',
    "J":'a',
    "R":'r'
}

#%%
def process(text, lemmatizer=nltk.stem.wordnet.WordNetLemmatizer()):
    """ Normalizes case and handles punctuation
    Inputs:
        text: str: raw text
        lemmatizer: an instance of a class implementing the lemmatize() method
                    (the default argument is of type nltk.stem.wordnet.WordNetLemmatizer)
    Outputs:
        list(str): tokenized text
    """
    #handle url
    text = re.sub(r'http\S+', '', text)
    
    #handle emoji
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    
    #handle apostrophe 's
    text = text.replace("'s","")

    #handle other apostrophe
    text = text.replace("'","")

    #handle all other punctuation
    text = re.sub(r'[' + string.punctuation + r']+', ' ', text).strip()

    #handle lowercase
    text = text.lower()

    tokens = word_tokenize(text)

    pos_tags = nltk.pos_tag(tokens)

    lemmatized_tokens = []
    for word, tag in pos_tags:
        wordnet_pos = get_wordnet_pos(tag)
        try:
            lemmatized_token = lemmatizer.lemmatize(word, pos=wordnet_pos)
            lemmatized_tokens.append(lemmatized_token)
        except Exception:
            pass

    return lemmatized_tokens

    
#%%
def get_wordnet_pos(treebank_tag): #no need to change this function - used to tag tokens for context specification and then for lemmatization
    if treebank_tag.startswith('J'):
        return nltk.corpus.wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return nltk.corpus.wordnet.VERB
    elif treebank_tag.startswith('R'):
        return nltk.corpus.wordnet.ADV
    else:
        return nltk.corpus.wordnet.NOUN
#%%
def process_all(df, lemmatizer=nltk.stem.wordnet.WordNetLemmatizer()):
    """ process all text in the dataframe using process function.
    Inputs
        df: pd.DataFrame: dataframe containing a column 'text' loaded from the CSV file
        lemmatizer: an instance of a class implementing the lemmatize() method
                    (the default argument is of type nltk.stem.wordnet.WordNetLemmatizer)
    Outputs
        pd.DataFrame: dataframe in which the values of text column have been changed from str to list(str),
                        the output from process_text() function. Other columns are unaffected.
    """
    df['Content'] = df['Content'].fillna('')
    df['Content'] = df['Content'].astype(str)
    processed_content = []

    for index, row in df.iterrows():
        content = process(row['Content'], lemmatizer)
        processed_content.append(content)
    
    df['Content'] = processed_content
    return df
    
#%%
def identity(x):
    return x
def create_features(processed_tweets, stop_words):
    """ creates the feature matrix using the processed tweet text
    Inputs:
        processed_tweets: pd.DataFrame: processed tweets read from train/test csv file, containing the column 'text'
        stop_words: list(str): stop_words by nltk stopwords (after processing)
    Outputs:
        sklearn.feature_extraction.text.TfidfVectorizer: the TfidfVectorizer object used
            we need this to tranform test tweets in the same way as train tweets
        scipy.sparse.csr.csr_matrix: sparse bag-of-words TF-IDF feature matrix
    """
    # convert the processed_tweets from pd.DataFrame to list
    tweet_texts = processed_tweets.tolist()
    #stop_words = [word.lower() for word in stop_words]

    # Create a TfidfVectorizer object
    vectorizer = TfidfVectorizer(
        tokenizer=identity,
        lowercase=False, 
        stop_words=stop_words, 
        min_df=2
    )
    
    feature_matrix = vectorizer.fit_transform(tweet_texts)
    return vectorizer, feature_matrix

#%%
def create_labels(processed_tweets):
    """ creates the class labels from handle
    Inputs:
        processed_tweets: pd.DataFrame: tweets read from train file, containing the column 'handle'
    Outputs:
        numpy.ndarray(int): dense binary numpy array of class labels
    """
    zero = ['realDonaldTrump', 'JDVance', 'GOP']
    array = []
    for item in  processed_tweets['handle']:
        if item in zero:
            array.append(0)
        else:
            array.append(1)
    binary_array = np.array(array, dtype=int)
    return binary_array
#%%
class MajorityLabelClassifier():
    """
    A classifier that predicts the mode of training labels
    """
    def __init__(self):
        """
        Initialize your parameter here
        """
        self.mode = None

    def fit(self, X, y):
        """
        Implement fit by taking training data X and their labels y and finding the mode of y
        i.e. store your learned parameter
        """
        self.mode = Counter(y).most_common(1)[0][0]

    def predict(self, X):
        """
        Implement to give the mode of training labels as a prediction for each data instance in X
        return labels
        """
        return np.full(X.shape[0], self.mode)

#%%
def learn_classifier(X_train, y_train, penalty):
    """ learns a classifier from the input features and labels using the penalty function supplied
    Inputs:
        X_train: scipy.sparse.csr.csr_matrix: sparse matrix of features, output of create_features()
        y_train: numpy.ndarray(int): dense binary vector of class labels, output of create_labels()
        penalty: str: penalty function to be used with classifier. [none|l2|l1|elasticnet]
    Outputs:
        sklearn.linear_model.LogisticRegression: classifier learnt from data
    """
    if penalty not in ['none', 'l2', 'l1', 'elasticnet']:
        raise ValueError("Invalid penalty. Must be one of ['none', 'l2', 'l1', 'elasticnet']")
    
    if penalty == 'none':
        solver = 'lbfgs'
    elif penalty == 'l2':
        solver = 'lbfgs'
    elif penalty == 'l1':
        solver = 'liblinear'
    elif penalty == 'elasticnet':
        solver = 'saga'
    

    classifier = LogisticRegression(
        penalty=None if penalty == 'none' else penalty,
        solver = solver,
        #max_iter=100,
        #random_state=42,
        l1_ratio=0.5 if penalty == 'elasticnet' else None
    )
    
    classifier.fit(X_train, y_train)
    return classifier
#%%
def evaluate_classifier(classifier, X_validation, y_validation):
    """ evaluates a classifier based on a supplied validation data
    Inputs:
        classifier: sklearn.linear_model.LogisticRegression: classifer to evaluate
        X_validation: scipy.sparse.csr.csr_matrix: sparse matrix of features
        y_validation: numpy.ndarray(int): dense binary vector of class labels
    Outputs:
        double: accuracy of classifier on the validation data
    """
    #4-fold cross-validation
    kf = KFold(n_splits=4)
    accuracies = []

    for train_index, test_index in kf.split(X_validation):
        X_train, X_test = X_validation[train_index], X_validation[test_index]
        y_train, y_test = y_validation[train_index], y_validation[test_index]
        
        y_prediction = classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_prediction)
        accuracies.append(accuracy)

    result_accuracy = np.mean(accuracies)
    return result_accuracy

#%%
def classify_tweets(tfidf, classifier, unlabeled_tweets):
    """ predicts class labels for raw tweet text
    Inputs:
        tfidf: sklearn.feature_extraction.text.TfidfVectorizer: the TfidfVectorizer object used on training data
        classifier: sklearn.linear_model.LogisticRegression: classifier learned
        unlabeled_tweets: pd.DataFrame: tweets read from tweets_test.csv
    Outputs:
        numpy.ndarray(int): dense binary vector of class labels for unlabeled tweets
    """
    tweets_text = unlabeled_tweets['Content']
    X_test = tfidf.transform(tweets_text)
    predicted_labels = classifier.predict(X_test)
    
    return predicted_labels