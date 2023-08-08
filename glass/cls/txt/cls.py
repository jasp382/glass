"""
Text Classification
"""

import pandas as pd
import numpy  as np
from glass.cls.txt import txt_to_num_representation

def model_selection(dataFile, refCol, dataCol, outTbl, lang='english', CV=5):
    """
    See which model is better to use in text classification for a specific
    data sample
    
    Compare:
    Logistic Regression (LogisticRegression)
    (Multinomial) Naive Bayes (MultinomialNB)
    Linear Support Vector Machine (LinearSVC)
    Random Forest (RandomForestClassifier)
    """
    
    import os
    from glass.pys.oss                   import fprop
    from glass.rd                        import tbl_to_obj
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model            import LogisticRegression
    from sklearn.ensemble                import RandomForestClassifier
    from sklearn.svm                     import LinearSVC
    from sklearn.naive_bayes             import MultinomialNB
    from sklearn.model_selection         import cross_val_score
    from glass.wt                        import obj_to_tbl
    
    # Data to DataFrame
    trainDf = tbl_to_obj(dataFile)
    
    # Just in case, delete rows with NULL refCol and NULL dataCol
    trainDf = trainDf[pd.notnull(trainDf[dataCol])]
    trainDf = trainDf[pd.notnull(trainDf[refCol])]
    
    # Ref col to integers
    trainDf['ref_id'] = trainDf[refCol].factorize()[0]
    
    # Text to numbers
    features = txt_to_num_representation(trainDf, dataCol, lang)
    
    labels = trainDf.ref_id
    
    """ Test Models """
    models = [
        RandomForestClassifier(n_estimators=200, max_depth=3, random_state=0),
        LinearSVC(),
        MultinomialNB(),
        LogisticRegression(random_state=0)
    ]
    
    cv_df = pd.DataFrame(index=range(CV * len(models)))
    entries = []
    
    for model in models:
        m_name = model.__class__.__name__
        accuracies = cross_val_score(
            model, features, labels, scoring='accuracy', cv=CV
        )
        
        for fold_idx, accuracy in enumerate(accuracies):
            entries.append((m_name, fold_idx, accuracy))
    
    # Create and Export evaluation table
    cv_df = pd.DataFrame(
        entries, columns=['model_name', 'fold_idx', 'accuracy'])
    cv_df_gp = pd.DataFrame(cv_df.groupby('model_name').accuracy.mean())
    cv_df_gp.reset_index(inplace=True)
    
    # Export Graphic
    import seaborn as sns
        
    a = sns.boxplot(x='model_name', y='accuracy', data=cv_df)
        
    b = sns.stripplot(
        x='model_name', y='accuracy', data=cv_df,
        size=10, jitter=True, edgecolor="gray", linewidth=2)
        
    fig = b.get_figure()
    fig.savefig(os.path.join(
        os.path.dirname(outTbl), fprop(outTbl, 'fn') + '.png'
    ))
    
    return obj_to_tbl(cv_df_gp, outTbl)


def text_prediction(trainData, classData, trainRefCol, trainClsCol, clsDataCol,
                    outfile, method='NaiveBayes', lang='english'):
    """
    Text classification
    
    Classifier Options:
    1) NaiveBayes;
    2) LinearSupportVectorMachine;
    3) RandomForest;
    4) LogisticRegression.
    """
    
    import pandas as pd
    from glass.rd import tbl_to_obj
    from glass.wt import obj_to_tbl
    
    # Data to Dataframe
    trainDf = tbl_to_obj(trainData) if type(trainData) != pd.DataFrame else  trainData
    classDf = tbl_to_obj(classData) if type(classData) != pd.DataFrame else classData
    
    # Just in case, delete rows with NULL refCol and NULL dataCol
    trainDf = trainDf[pd.notnull(trainDf[trainClsCol])]
    trainDf = trainDf[pd.notnull(trainDf[trainRefCol])]
    classDf = classDf[pd.notnull(classDf[clsDataCol])]
    
    if method == 'NaiveBayes':
        from sklearn.naive_bayes             import MultinomialNB
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.feature_extraction.text import TfidfTransformer
        
        """" Train Model """
        # X train is trainClsCol
        # Y train is trainRefCol
        x_train, y_train = trainDf[trainClsCol], trainDf[trainRefCol]
    
        count_vect = CountVectorizer()
    
        X_train_counts = count_vect.fit_transform(x_train)
    
        tfidf_transformer = TfidfTransformer()
    
        X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    
        clf = MultinomialNB().fit(X_train_tfidf, y_train)
    
        """ Predict """
        result = clf.predict(count_vect.transform(classDf[clsDataCol]))
    
        classDf['classification'] = result
    
    elif method == 'LinearSupportVectorMachine':
        from sklearn.svm import LinearSVC
        
        # Get features and Labels
        trainDf['ref_id'] = trainDf[trainRefCol].factorize()[0]
        labels = trainDf.ref_id
        
        features, tvect = txt_to_num_representation(
            trainDf, trainClsCol, __lang=lang, returnTfiDf=True)
        
        featTst = tvect.transform(classDf[clsDataCol])
        
        """ Train model """
        model = LinearSVC()
        
        model.fit(features, labels)
        
        y_pred = model.predict(featTst)
        
        classDf['classification'] = y_pred
        
        # Create Dataframe only with ref_id's, without duplicates
        ref_id_df = trainDf[[
            trainRefCol, 'ref_id'
        ]].drop_duplicates().sort_values('ref_id')
        ref_id_df.columns = ['class_name', 'ref_fid']
        
        classDf = classDf.merge(
            ref_id_df, how='inner',
            left_on='classification', right_on='ref_fid'
        )
        
        classDf.loc[:, 'classification'] = classDf.class_name
        
        classDf.drop(['ref_fid', 'class_name'], axis=1, inplace=True)
    
    elif method == 'RandomForest':
        from sklearn.ensemble import RandomForestClassifier
        # Get features
        
        features, tvect = txt_to_num_representation(
            trainDf, trainClsCol, __lang=lang, returnTfiDf=True)
        
        featTst = tvect.transform(classDf[clsDataCol])
        
        classifier = RandomForestClassifier(
            n_estimators=1000, random_state=0
        )
        classifier.fit(features, trainDf[trainRefCol])
        
        y_pred = classifier.predict(featTst)
        
        classDf['classification'] = y_pred
    
    elif method == 'LogisticRegression':
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.feature_extraction.text import TfidfTransformer
        from sklearn.pipeline                import Pipeline
        from sklearn.linear_model            import LogisticRegression
        
        logreg = Pipeline([
            ('vect', CountVectorizer()),
            ('tfidf', TfidfTransformer()),
            ('clf', LogisticRegression(n_jobs=1, C=1e5, multi_class='auto', solver='lbfgs')),
        ])
        
        logreg.fit(trainDf[trainClsCol], trainDf[trainRefCol])
        
        y_pred = logreg.predict(classDf[clsDataCol])
        
        classDf['classification'] = y_pred
    
    return obj_to_tbl(classDf, outfile)


def txtclsmdl_to_file(train, tRef, tData, outMdl, outTf,
                      method='NaiveBayes'):
    """
    Fit Text classification model and save model to file
    
    Classifier Options:
    1) NaiveBayes;
    2) LinearSupportVectorMachine;
    3) RandomForest;
    4) LogisticRegression.
    """
    
    import pandas as pd
    import joblib
    from glass.rd import tbl_to_obj
    
    # Data to Dataframe
    trainDf = tbl_to_obj(train) if type(train) != pd.DataFrame else  train
    
    # Just in case, delete rows with NULL refCol and NULL dataCol
    trainDf = trainDf[pd.notnull(trainDf[tData])]
    trainDf = trainDf[pd.notnull(trainDf[tRef])]
    
    if method == 'NaiveBayes':
        from sklearn.naive_bayes             import MultinomialNB
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.feature_extraction.text import TfidfTransformer
        
        """" Train Model """
        # X train is trainClsCol
        # Y train is trainRefCol
        x_train, y_train = trainDf[tData], trainDf[tRef]
    
        tvect = CountVectorizer()
    
        X_train_counts = tvect.fit_transform(x_train)
    
        tfidf_transformer = TfidfTransformer()
    
        X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    
        clf = MultinomialNB().fit(X_train_tfidf, y_train)
    
    elif method == 'LinearSupportVectorMachine':
        from sklearn.svm import LinearSVC
        
        feat, tvect = txt_to_num_representation(
            trainDf, tData, __lang='english', returnTfiDf=True)
        
        # Train model
        clf = LinearSVC().fit(feat, trainDf[tRef])
    
    elif method == 'RandomForest':
        from sklearn.ensemble import RandomForestClassifier
        
        feat, tvect = txt_to_num_representation(
            trainDf, tData, __lang='english', returnTfiDf=True)
        
        clf = RandomForestClassifier(n_estimators=1000, random_state=0)
        clf.fit(feat, trainDf[tRef])
    
    elif method == 'LogisticRegression':
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.feature_extraction.text import TfidfTransformer
        from sklearn.pipeline                import Pipeline
        from sklearn.linear_model            import LogisticRegression
        
        clf = Pipeline([
            ('vect', CountVectorizer()), ('tfidf', TfidfTransformer()),
            ('clf', LogisticRegression(
                n_jobs=1, C=1e5, multi_class='auto', solver='lbfgs'))
        ])
        
        clf.fit(trainDf[tData], trainDf[tRef])
    
    if method != 'LogisticRegression':
        joblib.dump(tvect, outTf)
        joblib.dump(clf, outMdl)
    
    else:
        joblib.dump(clf, outMdl)
        outTf=None
    
    return outMdl, outTf


def predict_fm_mdl(mdlFile, vFile, data, txtCol, method='NaiveBayes'):
    """
    Text classification using file with fit data
    """
    
    from joblib   import load
    import pandas as pd
    from glass.rd import tbl_to_obj
    
    classDf = tbl_to_obj(data) if type(data) != pd.DataFrame else data
    classDf = classDf[pd.notnull(classDf[txtCol])]
    
    clf   = load(mdlFile)
    tvect = None if not vFile else load(vFile)
    
    if method == 'NaiveBayes':
        result = clf.predict(tvect.transform(data[txtCol]))
        
        data.loc[:, 'classification'] = result
    
    elif method == 'LinearSupportVectorMachine':
        feaTst = tvect.transform(classDf[txtCol])
        
        y_pred = clf.predict(feaTst)
        
        data.loc[:, 'classification'] = y_pred
    
    elif method == 'RandomForest':
        feaTst = tvect.transform(classDf[txtCol])
        
        y_pred=clf.predict(feaTst)
        
        data.loc[:, 'classification'] = y_pred
    
    elif method == 'LogisticRegression':
        y_pred = clf.predict(classDf[txtCol])
        
        data.loc[:, 'classification'] = y_pred
    
    return data


"""
Query based methods
"""

def get_rows_related_with_event(db, tblSchema, words, resultTbl,
                                startTime=None, endTime=None):
    """
    Take a table of a database and see if the text in one column
    is related with some event. The relation between rows and event will
    be true when a set of words given as input exists in a row.
    
    tblSchema = {
        "TNAME"   : "facedata",
        "TEXTCOL" : "message",
        "TIMECOL" : "datahora",
        "SELCOL"  : [post_id, type],
        "TEXTCASE" : (
            "CASE WHEN type = 'link' THEN lower(unaccent(description)) "
            "ELSE lower(unaccent(message)) END"
        )
    }
    
    NOTE: only works for PostgreSQL
    """
    
    from glass.pys import obj_to_lst
    from glass.it  import db_to_tbl
    
    if "TNAME" not in tblSchema or "TEXTCOL" not in tblSchema:
        raise ValueError((
            "tblSchema input should be a dict with at least TNAME and TEXTCOL "
            "keys. The value of the first should be a table name; "
            "the value of the second shoulbe the name of a column with text "
            "to classify!"
        ))
    
    # Words to list
    words = obj_to_lst(words)
    
    cols = None if "SELCOL" not in tblSchema else obj_to_lst(tblSchema["SELCOL"])
    
    like_words = " OR ".join(["{} LIKE '%%{}%%'".format(
        tblSchema["TEXTCOL"], word) for word in words])
    
    time_where = "" if "TIMECOL" not in tblSchema or not startTime \
        or not endTime else (
            " {w} TO_TIMESTAMP({c}, 'YYYY-MM-DD HH24:MI:SS') > "
            "TO_TIMESTAMP('{l}', 'YYYY-MM-DD HH24:MI:SS') AND "
            "TO_TIMESTAMP({c}, 'YYYY-MM-DD HH24:MI:SS') < "
            "TO_TIMESTAMP('{h}', 'YYYY-MM-DD HH24:MI:SS')"
        ).format(
            w="WHERE" if "TEXTCASE" in tblSchema else "AND",
            c=tblSchema["TIMECOL"], l=startTime, h=endTime
        )
    
    Q = (
        "SELECT * FROM ("
            "SELECT {selCols} FROM {tbl}{timeWhr}"
        ") AS foo WHERE {wordsWhr}"
        ).format(
            tbl=tblSchema["TNAME"], wordsWhr=like_words,
            selCols="{} AS {}".format(
                tblSchema["TEXTCASE"], tblSchema["TEXTCOL"]
            ) if not cols else "{}, {} AS {}".format(
                ", ".join(cols), tblSchema["TEXTCASE"], tblSchema["TEXTCOL"]
            ),
            timeWhr=time_where
        ) if "TEXTCASE" in tblSchema else (
            "SELECT {selCols} FROM {tbl} WHERE ({wordsWhr}){timeWhr}"
        ).format(
            selCols=", ".join(cols + [tblSchema["TEXTCOL"]]),
            tbl=tblSchema["TNAME"], wordsWhr=like_words,
            timeWhr=time_where
            
        )
    
    return db_to_tbl(db, Q, resultTbl)
