"""
Word frequency analysis
"""

import pandas as pd
import numpy as np

def correlated_words(dataFile, refCol, dataCol, outTbl, lang='english', N=2,
                     refSheet=None):
    """
    Get words correlated with some text class 
    """
    
    from sklearn.feature_selection import chi2
    from glass.dct              import obj_to_tbl
    from glass.dct                 import tbl_to_obj
    from glass.cls.txt             import txt_to_num_representation
    
    # Data to DataFrame
    trainDf = tbl_to_obj(
        dataFile, sheet=refSheet
    ) if type(dataFile) != pd.DataFrame else dataFile
    
    # Just in case, delete rows with NULL refCol and NULL dataCol
    trainDf = trainDf[pd.notnull(trainDf[dataCol])]
    trainDf = trainDf[pd.notnull(trainDf[refCol])]
    
    """
    Add a column encoding the reference classes as an integer because
    categorical variables are often better represented by integers
    than strings
    """
    
    from io import StringIO
    
    # Get a ID for Ref/text classes values
    trainDf['ref_id'] = trainDf[refCol].factorize()[0]
    
    # Create Dataframe only with ref_id's, without duplicates
    ref_id_df = trainDf[[refCol, 'ref_id']].drop_duplicates().sort_values(
        'ref_id'
    )
    
    # Create dicts to easy relate ref_id with ref_value
    ref_to_id = dict(ref_id_df.values)
    id_to_ref = dict(ref_id_df[['ref_id', refCol]].values)
    
    """
    Text to numbers
    """
    features, tfidf = txt_to_num_representation(
        trainDf, dataCol, lang, returnTfiDf=True)
    
    labels = trainDf.ref_id
    
    """
    Get most correlated words
    """
    
    corr_words = []
    for ref_name, ref_id in sorted(ref_to_id.items()):
        features_chi2 = chi2(features, labels == ref_id)
        
        indices = np.argsort(features_chi2[0])
        
        feat_names = np.array(tfidf.get_feature_names())[indices]
        
        unigrams = [v for v in feat_names if len(v.split(' ')) == 1][-N:]
        bigrams  = [v for v in feat_names if len(v.split(' ')) == 2][-N:]
        cols_d = [ref_name] + unigrams + bigrams
        
        corr_words.append(cols_d)
    
    COLS_NAME = ['ref_name'] + [
        'unigram_{}'.format(str(i+1)) for i in range(N)
    ] + [
        'bigram_{}'.format(str(i+1)) for i in range(N)
    ]
    dfCorrWords = pd.DataFrame(corr_words,columns=COLS_NAME)
    
    return obj_to_tbl(dfCorrWords, outTbl)

