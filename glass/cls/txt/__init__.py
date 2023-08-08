"""
Text Classification
"""

def txt_to_num_representation(df, txtCol, __lang, returnTfiDf=None):
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
    
    tfidf = TfidfVectorizer(
        sublinear_tf=True, min_df=5,
        norm='l2', encoding='latin-1',
        ngram_range=(1,2), stop_words=__lang
    )
    
    features = tfidf.fit_transform(df[txtCol]).toarray()
    
    if returnTfiDf:
        return features, tfidf
    else:
        return features

