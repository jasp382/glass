from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

from rest_framework  import generics
from geotmlnh.models import facedata
from geotmlnh.serial import CFaceSerial


class FaceDataView(generics.ListAPIView):
    """
    View Facebook Data
    """
    
    serializer_class = CFaceSerial
    
    def get_queryset(self):
        return facedata.objects.all()[:2000]


"""
Views for data sanitazing - pre processamento
"""

def face_pp(request):
    """
    Face data sanitize
    
    Sanitize data to use in classification
    """
    
    from geotmlnh        import API_KEY
    from api.settings    import DATABASES
    from geotmlnh.schema import FACEBOOK_SCHEMA as TBL_SCHEMA
    from glass.sql.fm     import q_to_obj
    from glass.sql.prop      import check_last_id
    from glass.sql.to     import df_to_db
    
    if 'key' not in request.GET or request.GET['key'] != API_KEY:
        from django.http import HttpResponseForbidden
        
        return HttpResponseForbidden()
    
    DB = DATABASES['default']
    
    Q1 = (
        "(SELECT *, to_tsvector('{ts_dict}', regexp_replace("
            "regexp_replace(lower({useUn}txtcls{useUnn}), 'http://[^:\s]+(\S+)', "
            "' ', 'g'), '[^\w]+', ' ', 'g')) "
        "AS txtsan FROM ("
            "SELECT {t}.{pk}, {t}.{t_id}, {txtcol} AS txtcls, "
            "{dt}.{timecol} AS datahora, {t}.{refcol} "   
            "FROM {t} INNER JOIN {dt} ON "
            "{t}.{t_id} = {dt}.{dt_id} "
            "LEFT JOIN {txtTbl} ON {t}.{pk} = {txtTbl}.{txtFK} "
            "WHERE {txtTbl}.{txtFK} IS NULL"
        ") AS foo) AS stop_table"
    )
    
    Q2 = (
        "SELECT {pk}, ARRAY_TO_STRING(array_agg("
            "word ORDER BY word_index), ' ', '*') AS txtsan "
        "FROM ("
            "SELECT fid, word, CAST(UNNEST(word_index) AS integer) "
            "AS word_index FROM ("
                "SELECT fid, SPLIT_PART(tst, ';', 1) AS word, "
                "STRING_TO_ARRAY(SPLIT_PART(tst, ';', 2), ',') AS word_index FROM ("
                    "SELECT fid, REPLACE(REPLACE(REPLACE(REPLACE(REPLACE("
                        "CAST(UNNEST(txtsan) AS text), "
                            "',{{', ',\"{{'), ',\"{{', ';'), '}}\"', ''), "
                            "'(', ''), '}}', '') AS tst "
                        "FROM {tbl}"
                    ") AS foo"
                ") AS foo2"
        ") AS foo3 INNER JOIN {tbl} ON foo3.fid = stop_table.fid "
        "GROUP BY {pk}, stop_table.txtcls"
    )
    
    Q3 = (
        "SELECT {pk} AS {rid}, pp_one.txtsan AS full_pp, pp_two.txtsan AS txt_pp "
        "FROM ({tbl_one}) AS pp_one INNER JOIN ({tbl_two}) AS pp_two "
        "ON pp_one.fid = pp_two.fid" 
    ).format(
        pk="pp_one.{}".format(TBL_SCHEMA['SAMPLE_PK']),
        rid = TBL_SCHEMA['SAMPLE_TXT_FK'],
        tbl_one=Q2.format(
            tbl=Q1.format(
                pk=TBL_SCHEMA['SAMPLE_PK'],
                ts_dict='portuguese', useUn="unaccent(", useUnn=")",
                txtcol=TBL_SCHEMA['TXT_COL'], t=TBL_SCHEMA['SAMPLE_T'],
                dt=TBL_SCHEMA['DATA_T'], t_id=TBL_SCHEMA['SAMPLE_FK'],
                dt_id=TBL_SCHEMA['DATA_ID'], timecol=TBL_SCHEMA['TIME_COL'],
                refcol=TBL_SCHEMA['REF_COL'], txtTbl=TBL_SCHEMA['SAMPLE_TXT_T'],
                txtFK=TBL_SCHEMA['SAMPLE_TXT_FK']
            ), pk="stop_table.{}".format(TBL_SCHEMA['SAMPLE_PK'])
        ),
        tbl_two=Q2.format(
            tbl=Q1.format(
                pk=TBL_SCHEMA['SAMPLE_PK'],
                ts_dict='simple_portuguese', useUn="", useUnn="",
                txtcol=TBL_SCHEMA['TXT_COL'], t=TBL_SCHEMA['SAMPLE_T'],
                dt=TBL_SCHEMA['DATA_T'], t_id=TBL_SCHEMA['SAMPLE_FK'],
                dt_id=TBL_SCHEMA['DATA_ID'], timecol=TBL_SCHEMA['TIME_COL'],
                refcol=TBL_SCHEMA['REF_COL'], txtTbl=TBL_SCHEMA['SAMPLE_TXT_T'],
                txtFK=TBL_SCHEMA['SAMPLE_TXT_FK']
            ), pk="stop_table.{}".format(TBL_SCHEMA['SAMPLE_PK'])
        )
    )
    
    dt_ref = q_to_obj(DB, Q3)
    
    LAST_FID = check_last_id(DB, TBL_SCHEMA['SAMPLE_TXT_PK'], TBL_SCHEMA['SAMPLE_TXT_T'])
    
    dt_ref[TBL_SCHEMA['SAMPLE_TXT_PK']] = dt_ref.index + LAST_FID + 1
    
    df_to_db(DB, dt_ref, TBL_SCHEMA['SAMPLE_TXT_T'], append=True, api='psql')
    
    return HttpResponse('resultou')


def train_classifiers(request):
    """
    Train classifiers
    
    The best classifier will be avaiable to classify text
    """
    
    from geotmlnh import API_KEY
    
    if 'key' not in request.GET or request.GET['key'] != API_KEY:
        from django.http import HttpResponseForbidden
        
        return HttpResponseForbidden()
    
    import datetime
    import os; import numpy;  import random
    from glass.sql.fm          import q_to_obj
    from glass.adv.txtcls.cls  import txtclsmdl_to_file
    from glass.adv.txtcls.cls  import predict_fm_mdl
    from glass.adv.txtcls.eval import binary_eval
    from glass.pys.df.stats    import df_to_freqdf
    from glass.pys.df.mng      import merge_df
    from glass.pys.tm          import now_as_str
    from glass.sql.prop           import check_last_id
    from glass.sql.to          import df_to_db
    from api.settings         import DATABASES
    from geotmlnh             import MDL_LOG
    from geotmlnh.schema      import REFDATA_SCHEMA as SCHEMA
    from geotmlnh.models      import classi, class_res
    
    # Get RQST_ID
    RQST_FID = now_as_str()
    
    # Get Parameters to Connect to Database
    DB = DATABASES['default']
    
    # Global Variables
    TRAIN_DIM = 70; N_ITERA = 10
    
    TBL     =   SCHEMA["TABLE"]; txtTBL   = SCHEMA["SAMPLE_TXT_T"]
    PK      =      SCHEMA['PK']; FK       = SCHEMA["SAMPLE_TXT_FK"]
    REF_COL = SCHEMA['REF_COL']; DATA_COL = SCHEMA['DATA_COL']
    
    Q = (
        "SELECT rd.*, reftxt.{dataCol} "
        "FROM {refTbl} AS rd INNER JOIN {txtTbl} AS reftxt "
        "ON rd.{pk} = reftxt.{fk}"
    ).format(
        dataCol=DATA_COL, refTbl=TBL, txtTbl=txtTBL,
        pk=PK, fk=FK
    )
    
    # Get Reference Table
    dt_ref = q_to_obj(DB, Q, db_api='psql')
    
    """
    Produce frequencies table counting the number of each reference value
    
      | REF_COL | COUNT
    0 |    0    | 1931
    1 |    1    |  560
    
    After count the number of rows for trainning
      | REF_COL | COUNT | n_train
    0 |    0    | 1931  |  1352 (70% of 1931) - this if TRAIN_DIM = 70
    1 |    1    |  560  |   392 (70% of 560)
    """
    refCount = df_to_freqdf(dt_ref, REF_COL)
    
    refCount['n_train'] = (refCount['count'] * TRAIN_DIM) / 100
    refCount            = refCount.round({'n_train' : 0})
    refCount['n_train'] = refCount.n_train.astype(int)
    refCount['count']   = refCount['count'].astype(int)
    
    """
    ROW NUMBER Function: give a number to the rows of each REF VALUE
    """
    dt_ref['RN'] = dt_ref.sort_values(
        [REF_COL], ascending=[True]
    ).groupby([REF_COL]).cumcount() + 1
    
    """
    Run Models:
    """
    mdls = {
        'NB' : 'NaiveBayes', 'SVM' :'LinearSupportVectorMachine',
        'RF' : 'RandomForest', 'LOGREG':'LogisticRegression'
    }
    
    sintese = {}
    for i in range(N_ITERA):
        # Create Random samples for train and test
        for idx, row in refCount.iterrows():
            rnd_train = random.sample(
                range(1, int(row['count'] + 1)), int(row.n_train))
            
            dt_ref['is_train'] = numpy.where(
                (dt_ref[REF_COL] == row[REF_COL]) & numpy.isin(
                    dt_ref.RN, rnd_train
                ), 1, 0 if idx == 0 else dt_ref.is_train
            )
        
        dt_test  = dt_ref[dt_ref.is_train == 0]
        dt_train = dt_ref[dt_ref.is_train == 1]
        
        for m in mdls:
            mdl, tfdif = txtclsmdl_to_file(
                dt_train, REF_COL, DATA_COL,
                os.path.join(MDL_LOG, 'mdl_{}_{}_{}.joblib'.format(
                    RQST_FID, m, str(i))),
                os.path.join(MDL_LOG, 'tfid_{}_{}_{}.joblib'.format(
                    RQST_FID, m, str(i))),
                method=mdls[m]
            )
            
            res = predict_fm_mdl(mdl, tfdif, dt_test, DATA_COL, method=mdls[m])
            
            confTbl, measuresTbl, resTbl = binary_eval(
                res, PK, REF_COL, res.copy(), PK, tstCol='classification'
            )
            
            dfTrain = dt_train[[PK]]
            dfTest  = res[[PK, "classification"]]
            
            if m not in sintese:
                sintese[m] = {i : {
                    "TRAIN"     : dfTrain, "TEST_CLS" : dfTest,
                    "CONFIANCE" : confTbl.copy(),
                    "MEASURES"  : measuresTbl.copy(),
                    "MDL_FILE"  : mdl, "VECT" : tfdif,
                    "ACC"       : round(float(
                        measuresTbl[measuresTbl.eval_mesure == 'Accuracy'].value * 100
                    ), 3)
                }}
            else:
                sintese[m][i] = {
                    "TRAIN"     : dfTrain, "TEST_CLS" : dfTest,
                    "CONFIANCE" : confTbl.copy(),
                    "MEASURES"  : measuresTbl.copy(),
                    "MDL_FILE"  : mdl, "VECT" : tfdif,
                    "ACC"       : round(float(
                        measuresTbl[measuresTbl.eval_mesure == 'Accuracy'].value * 100
                    ), 3)
                }
    
    # Get BEST MODEL
    bestMdl = {}
    for m in sintese:
        for i in sintese[m]:
            if not i:
                bestMdl[m] = i
            else:
                if sintese[m][i]["ACC"] > sintese[m][bestMdl[m]]["ACC"]:
                    bestMdl[m] = i
                else: continue
    
    # Save things in Database
    clsInst = classi.objects.create(
        fid = RQST_FID, nb_acc=sintese['NB'][bestMdl['NB']]["ACC"],
        nb_mdl=sintese['NB'][bestMdl['NB']]["MDL_FILE"],
        nb_vec=sintese['NB'][bestMdl['NB']]["VECT"],
        rf_acc=sintese['RF'][bestMdl['RF']]["ACC"],
        rf_mdl=sintese['RF'][bestMdl['RF']]["MDL_FILE"],
        rf_vec=sintese['RF'][bestMdl['RF']]["VECT"],
        svm_acc=sintese['SVM'][bestMdl['SVM']]["ACC"],
        svm_mdl=sintese['SVM'][bestMdl['SVM']]["MDL_FILE"],
        svm_vec=sintese['SVM'][bestMdl['SVM']]["VECT"],
        logreg_acc=sintese['LOGREG'][bestMdl['LOGREG']]["ACC"],
        logreg_mdl=sintese['LOGREG'][bestMdl['LOGREG']]["MDL_FILE"],
        daytime=datetime.datetime.now().replace(microsecond=0)
    )
    dfsTrain = []; dfsTest = []
    k = 0
    for m in sintese:
        MDL_NAME = mdls[m]
        for i in sintese[m]:
            __fid =RQST_FID + '_' + str(k) +  '_' + str(i)
            resI = class_res.objects.create(
                fid = __fid,
                cls_id = clsInst,
                mdl = MDL_NAME,
                mdlfil = sintese[m][i]["MDL_FILE"],
                vect   = 'None' if not sintese[m][i]["VECT"] else sintese[m][i]["VECT"],
                acc    = sintese[m][i]["ACC"],
                err    = round(float(
                    sintese[m][i]["MEASURES"][
                        sintese[m][i]["MEASURES"].eval_mesure == 'Error rate'].value * 100
                ), 3),
                tpr    = round(float(
                    sintese[m][i]["MEASURES"][
                        sintese[m][i]["MEASURES"].eval_mesure == 'Sensitivity'].value * 100
                ), 3),
                tnr    = round(float(
                    sintese[m][i]["MEASURES"][
                        sintese[m][i]["MEASURES"].eval_mesure == 'Specificity'].value * 100
                ), 3),
                ppr    = round(float(
                    sintese[m][i]["MEASURES"][
                        sintese[m][i]["MEASURES"].eval_mesure == 'Precision'].value * 100
                ), 3),
                fpr    = round(float(
                    sintese[m][i]["MEASURES"][
                        sintese[m][i]["MEASURES"].eval_mesure == 'False positive rate'].value * 100
                ), 3),
            )
            sintese[m][i]["TRAIN"]['fid_cls']    = __fid
            sintese[m][i]["TRAIN"].rename(columns={PK: 'fid_ref'}, inplace=True)
            sintese[m][i]["TEST_CLS"]['fid_cls'] = __fid
            sintese[m][i]["TEST_CLS"].rename(columns={PK : 'fid_ref'}, inplace=True)
            
            dfsTrain.append(sintese[m][i]["TRAIN"])
            dfsTest.append(sintese[m][i]["TEST_CLS"])
        
        k += 1
    
    # Update class_train e class_test
    dfClassTrain = merge_df(dfsTrain)
    lastID = check_last_id(DB, "fid", "geotmlnh_class_train")
    dfClassTrain["fid"] = dfClassTrain.index + lastID + 1 
    dfClassTest  = merge_df(dfsTest)
    lastID = check_last_id(DB, "fid", "geotmlnh_class_test")
    dfClassTest["fid"] = dfClassTest.index + lastID + 1
    df_to_db(DB, dfClassTrain, "geotmlnh_class_train", append=True, api='psql')
    df_to_db(DB, dfClassTest, "geotmlnh_class_test", append=True, api='psql')
    
    return HttpResponse('resultou')


def classify_endpnt(request):
    """
    Classify text
    """
    
    import nltk; import pandas
    from glass.adv.txtcls.cls import predict_fm_mdl
    from geotmlnh.models     import classi
    
    mdl = classi.objects.latest('daytime')
    
    txt = request.GET['txt'].replace('+', ' ')
    
    stopwords = nltk.corpus.stopwords.words('portuguese')
    
    mdls = {
        'NB' : 'NaiveBayes', 'SVM' :'LinearSupportVectorMachine',
        'RF' : 'RandomForest', 'LOGREG':'LogisticRegression'
    }; mdlFiles = {
        'NB' : mdl.nb_mdl, 'SVM' : mdl.svm_mdl, 'RF' : mdl.rf_mdl,
        'LOGREG' : mdl.logreg_mdl
    }; vecFiles = {
        'NB' : mdl.nb_vec, 'SVM' : mdl.svm_vec, 'RF' : mdl.rf_vec,
        'LOGREG' : None
    }
    
    sentences = nltk.sent_tokenize(txt, language='portuguese')
    for s in range(len(sentences)):
        words = nltk.word_tokenize(sentences[s], language='portuguese')
        
        __words = []
        for w in words:
            if w in stopwords:
                continue
            else:
                __words.append(w)
        
        sentences[s] = " ".join(__words)
    txt = " ".join(sentences)
    
    df_test = pandas.DataFrame([[1, txt]], columns=['fid', 'txt'])
    
    results = {}
    for m in mdls:
        res = predict_fm_mdl(
            mdlFiles[m], vecFiles[m], df_test, 'txt', method=mdls[m])
        
        res.rename(columns={'classification' : m}, inplace=True)
        results[m] = res.to_dict(orient="records")
    
    i = 0
    for m in mdls:
        if not i:
            mainRes = results[m]
        else:
            mainRes[0][m] = results[m][0][m]
    
    return HttpResponse(mainRes, content_type='json')


"""
Events Related
"""

from geotmlnh.serial import FireEventsSerial
from geotmlnh.models import fevents

class FireEventsLst(generics.ListAPIView):
    """
    List Fire Events
    """
    
    serializer_class = FireEventsSerial
    
    def get_queryset(self):
        return fevents.objects.all()
