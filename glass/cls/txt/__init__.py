"""
Text Classification
"""

import re

def osm_tokenizer(s):
    # divide por = ; : / - _ . , | e espaços ; retorna tokens lowercase
    tokens = re.split(r'[=\s;:/\-\._\|,]+', str(s))
    return [t.lower() for t in tokens if t]


def txt_to_num_representation(df, txtCol, __lang, returnTfiDf=None, osm_use_case=None):
    """
    Sanitize text representation

    Text to Numbers and noise deletion
    
    sublinear_df is set to True to use a logarithmic form for frequency.

    min_df is the minimum numbers of documents a word must
    be present in to be kept.

    norm is set to l2, to ensure all our feature vectors have
    a euclidian norm of 1.

    ngram_range is set to (1, 2) to indicate that we want
    to consider both unigrams and bigrams.

    stop_words is set to "english" to remove all common
    pronouns ("a", "the", ...) to reduce the number of noisy features.
    """
    
    from sklearn.feature_extraction.text import TfidfVectorizer

    if not osm_use_case:
    
        tfidf = TfidfVectorizer(
            sublinear_tf=True, min_df=5,
            norm='l2', encoding='latin-1',
            ngram_range=(1,2), stop_words=__lang
        )
    
    else:
        tfidf = TfidfVectorizer(
            tokenizer=osm_tokenizer,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True,
            use_idf=True,
            norm='l2',
            lowercase=True
        )
    
    features = tfidf.fit_transform(df[txtCol]).toarray()
    
    if returnTfiDf:
        return features, tfidf
    else:
        return features

