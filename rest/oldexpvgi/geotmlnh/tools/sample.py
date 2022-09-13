# -*- coding: utf-8 -*-

"""
Criação orientada de amostra de referencia

O objectivo é garantir que na amostra de referencia existam:

1 - linhas com palavras de interesse e geonames;

2 - linhas com palavras de interesse;

3 - linhas com geonames e sem palavras de interesse;

4 - linhas sem palavras de interesse e sem geonames.
"""

import argparse

def arg_parsing():
    parser = argparse.ArgumentParser(
        description='Data sample creation'
    )
    
    
    parser.add_argument('path_out_file', help=(
        'Absolute path to output file (.xlsx)'
    ))
    
    return parser.parse_args()


"""
Create sample Method
"""

def get_sample(CON_PGSQL, WORD_SCHEMA, DATA_SCHEMA, OUTFILE,
               FACE_PAGES=None, SPLIT_IN=1, GEONAME_SCHEMA=None,
               SAMPLE_MAX_SIZE=None):
    """
    Parametros obrigatorios:
    
    CON_PGSQL = {
        "HOST" : "localhost", "PORT" : "5432", "DATABASE" : "dsn_collect",
        "USER" : "postgres", "PASSWORD" : "admin"
    } # Elementos necessarios para conectar ao PostgreSQL
    
    # dict com algumas informacoes sobre a tabela que contem informacao
    # sobre a tabela em que estao registadas palavras de interesse, 
    # relacionadas com eventos extremos
    WORD_SCHEMA = {
        "TNAME" : "nome_da_tabela",
        "WORD"  : "nome_da_coluna_em_que_se_encontram_as_palavras"
        "GRP_FK" : "group_id",
        "TGROUP" : "word_groups",
        "GRP_FID": "grp_id",
        "GROUP"  : "description",
        "GRP_FILTER" : "fire"
    }
    
    # dict com algumas informacoes sobre a tabela que contem informacao
    # sobre a ocorrencia de eventos extremos
    # e.g. facedata ou twitterdata
    DATA_SCHEMA = {
        "TNAME" : nome da tabela ou query,
        "FID"   : nome da coluna com o ID do contributo,
        "TEXT_COL" : nome da coluna com o texto que descreve a ocorrencia de
            um evento
        "TIME"     : nome da coluna com data e hora,
        "OTHER_COLS  : "lista com o nome de colunas que devem constar na
            tabela da amostra",
        "LOWER_TIME" : "limite inferior do período a considerar",
        "HIGH_TIME"  : "limite superior do período a considerar",
        "PAGE_REF"   : "nome da coluna com o nome da página do facebook
            da qual os dados foram retirados",
    }
    
    OUTFILE = caminho para o ficheiro de saída. deve ser um ficheiro excel
        com extensão xlsx
    
    Parametros opcionais:
    
    FACE_PAGES = lista com o nome das paginas do facebook a considerar na
        criacao da amostra de referencia
    
    SPLIT_IN = Inteiro que indica o numero de sheets que o ficheiro de saida
        devera ter; as linhas da amostra serao distribuidas pelos varios sheets
    
    SAMPLE_MAX_SIZE = numero maximo de linhas que amostra pode ter
    
    # Dicionario com informacoes na tabela com GEONAMES
    GEONAME_SCHEMA = {
        "TNAME" : "Nome da tabela com geonames",
        "GEONAME : "Nome da coluna com os geonames"
    }
    """
    
    import pandas;         import os
    from glass.sql.fm       import q_to_obj
    from glass.to           import obj_to_tbl
    from glass.pys.df.split import split_df_inN
    from glass.sql.prop        import row_num
    from glass.sql.q  import q_to_ntbl, del_tables, tbls_to_tbl
    
    ROW_COUNT = {}
    
    # Del tables
    del_tables(CON_PGSQL, [
        'sss_like', 'sss_unlike', 'sss_like_w_g',
        'sss_like_w', 'sss_like_g', 'sss_full' 
    ])
    
    # Get Reference Words related with Extreme events
    Q = "SELECT {} AS word FROM {}".format(
        WORD_SCHEMA["WORD"], WORD_SCHEMA["TNAME"]
    ) if "GRP_FILTER" not in WORD_SCHEMA else (
        "SELECT {wt}.{w} AS word FROM {wt} INNER JOIN {gt} ON "
        "{wt}.{wt_grpid} = {gt}.{gt_grpid} "
        "WHERE {gt}.{grp_name} = '{group}'"
    ).format(
        wt=WORD_SCHEMA["TNAME"], w=WORD_SCHEMA["WORD"],
        gt=WORD_SCHEMA["TGROUP"], wt_grpid=WORD_SCHEMA["GRP_FK"],
        gt_grpid=WORD_SCHEMA["GRP_FID"], grp_name=WORD_SCHEMA["GROUP"],
        group=WORD_SCHEMA["GRP_FILTER"]
    )
    
    # Get sample tables
    page_ref_whr = None if "PAGE_REF" not in DATA_SCHEMA else \
        " OR ".join(["{}='{}'".format(
            DATA_SCHEMA["PAGE_REF"], p
        ) for p in FACE_PAGES]) if FACE_PAGES else None
    
    __TBL = ("("
        "SELECT * FROM {t} "
        "WHERE TO_TIMESTAMP({timeCol}, 'YYYY-MM-DD HH24:MI:SS') > "
        "TO_TIMESTAMP('{lowerTime}', 'YYYY-MM-DD HH24:MI:SS') AND "
        "TO_TIMESTAMP({timeCol}, 'YYYY-MM-DD HH24:MI:SS') < "
        "TO_TIMESTAMP('{highTime}', 'YYYY-MM-DD HH24:MI:SS'){ref}"
    ") AS jtbl").format(
        timeCol=DATA_SCHEMA["TIME"],
        lowerTime=DATA_SCHEMA["LOWER_TIME"],
        highTime=DATA_SCHEMA["HIGH_TIME"],
        t=DATA_SCHEMA["TNAME"],
        ref="" if not page_ref_whr else " AND ({})".format(page_ref_whr)
    )
    
    SEL_COLS = (
        "{fidCol}, lower(REPLACE(REPLACE(REPLACE(regexp_replace("
            "REPLACE(REPLACE(REPLACE(regexp_replace("
            "unaccent({txtCol}), 'https://[^:\s]+(\S+)', '', 'g'), ' ', 'XXX'), '.', 'YYY'), "
            "'-', 'ZZZ'), '[^\w+]', '', 'g'), 'XXX', ' '), 'YYY', '.'), "
            "'ZZZ', '-')) AS {txtCol}, {txtCol} AS {txtCol}_original, "
        "{timeCol}, {ocols}"
    ).format(
        fidCol=DATA_SCHEMA["FID"], txtCol=DATA_SCHEMA["TEXT_COL"],
        timeCol=DATA_SCHEMA["TIME"], ocols=", ".join(DATA_SCHEMA["OTHER_COLS"])
    )
    
    wordsInterest  = q_to_obj(CON_PGSQL, Q, db_api='psql')
    geonames = None if not GEONAME_SCHEMA else q_to_obj(CON_PGSQL, (
        "SELECT regexp_replace(unaccent({}), '[^a-zA-Z0-9]+', ' ', 'g') "
        "AS geoname FROM {}"
    ).format(GEONAME_SCHEMA["GEONAME"], GEONAME_SCHEMA["TNAME"]))
    
    wordsInterest["whr"] = DATA_SCHEMA["TEXT_COL"] + " LIKE '%" + \
        wordsInterest.word + "%'"
    wordsInterest["whr_not"] = DATA_SCHEMA["TEXT_COL"] + " NOT LIKE '%" + \
        wordsInterest.word + "%'"
    
    WHERE_LIKE_REF_WORDS = str(wordsInterest.whr.str.cat(sep= " OR "))
    WHERE_NOT_LIKE_REF_WORDS = str(wordsInterest.whr_not.str.cat(sep= " AND "))
    
    if type(geonames) != pandas.DataFrame:
        wtbl = q_to_ntbl(CON_PGSQL, 'sss_like', (
            "SELECT {selcos} FROM {tbl} WHERE {whr}{lm}"
        ).format(
            selcos=SEL_COLS, tbl=__TBL,
            whr=WHERE_LIKE_REF_WORDS,
            lm="" if not SAMPLE_MAX_SIZE else " LIMIT {}".format(
                str(int(SAMPLE_MAX_SIZE)/2))
        ))
        
        NROWS_LIKE = row_num(
            CON_PGSQL, wtbl
        ) if not SAMPLE_MAX_SIZE else int(SAMPLE_MAX_SIZE) / 2
        
        notwtbl = q_to_ntbl(CON_PGSQL, 'sss_unlike', (
            "SELECT {selcos} FROM {tbl} WHERE {whr} LIMIT {nrow}"
        ).format(
            selcos=SEL_COLS, tbl=__TBL,
            whr=WHERE_NOT_LIKE_REF_WORDS,
            nrow=NROWS_LIKE
        ))
        
        ROW_COUNT['N_ROW_LIKE'] = NROWS_LIKE if not SAMPLE_MAX_SIZE else row_num(
            CON_PGSQL, wtbl
        )
        ROW_COUNT['N_ROW_NOT_LIKE'] = row_num(CON_PGSQL, notwtbl)
        
        TMP_TABLES = [wtbl, notwtbl]
    
    else:
        geonames["whr"] = DATA_SCHEMA["TEXT_COL"] + " LIKE '%" + \
            geonames.geoname + "%'"
        geonames["whr_not"] = DATA_SCHEMA["TEXT_COL"] + " NOT LIKE '%" + \
            geonames.geoname + "%'"
        
        WHERE_LIKE_GEONAMES = str(geonames.whr.str.cat(sep=" OR "))
        WHERE_NOT_LIKE_GEONAMES = str(geonames.whr_not.str.cat(sep=" AND "))
        
        limit_q = "" if not SAMPLE_MAX_SIZE else " LIMIT {}".format(
            str(int(SAMPLE_MAX_SIZE/4)))
        
        # Select Rows with Interest Words and GEO ref
        word_geo_ref = q_to_ntbl(CON_PGSQL, 'sss_like_w_g', (
            "SELECT {selcos} FROM {tbl} WHERE ({words}) AND ({geon}){lm}"
        ).format(
            selcos=SEL_COLS, tbl=__TBL,
            words=WHERE_LIKE_REF_WORDS,
            geon=WHERE_LIKE_GEONAMES,
            lm=limit_q
        ))
        
        NROWS_WORD_GEO = row_num(
            CON_PGSQL, word_geo_ref
        ) if SAMPLE_MAX_SIZE else None
        
        # Select Rows with Interest Words and without GEO ref
        word_ref = q_to_ntbl(CON_PGSQL, 'sss_like_w', (
            "SELECT {selcos} FROM {tbl} WHERE ({words}) AND {geon}{lm}"
        ).format(
            selcos=SEL_COLS, tbl=__TBL,
            words=WHERE_LIKE_REF_WORDS,
            geon=WHERE_NOT_LIKE_GEONAMES,
            lm=limit_q if not NROWS_WORD_GEO or NROWS_WORD_GEO == int(SAMPLE_MAX_SIZE/4) \
                else " LIMIT {}".format(
                int(SAMPLE_MAX_SIZE/4) + (int(SAMPLE_MAX_SIZE/4) - NROWS_WORD_GEO)
            )
        ))
        
        NROWS_WORD = row_num(
            CON_PGSQL, word_ref
        ) if SAMPLE_MAX_SIZE else None
        
        SAMPLE_MAX_SIZE = (NROWS_WORD + NROWS_WORD_GEO) * 2 \
            if NROWS_WORD and NROWS_WORD_GEO else SAMPLE_MAX_SIZE
        
        limit_q = "" if not SAMPLE_MAX_SIZE else " LIMIT {}".format(
            str(int(SAMPLE_MAX_SIZE/4)))
        
        # Select Rows without Interest Words but with GEO ref
        geo_ref = q_to_ntbl(CON_PGSQL, 'sss_like_g', (
            "SELECT {selcos} FROM {tbl} WHERE ({words}) AND ({geon}){lm}"
        ).format(
            selcos=SEL_COLS, tbl=__TBL,
            words=WHERE_NOT_LIKE_REF_WORDS, geon=WHERE_LIKE_GEONAMES,
            lm=limit_q
        ))
        
        TMP_TABLES = [word_geo_ref, word_ref, geo_ref]
        
        # Select Rows without Interest Words and without GEO ref
        limit_N = [row_num(CON_PGSQL, i) for i in TMP_TABLES]
        
        ROW_COUNT['N_ROW_LIKE_W_G'] = limit_N[0]
        ROW_COUNT['N_ROW_LIKE_W']   = limit_N[1]
        ROW_COUNT['N_ROW_LIKE_G']   = limit_N[2]
        
        non_ref = q_to_ntbl(CON_PGSQL, 'sss_unlike', (
            "SELECT {selcos} FROM {tbl} WHERE {words} AND {geon} "
            "LIMIT {lm}"
        ).format(
            selcos=SEL_COLS, tbl=__TBL,
            words=WHERE_NOT_LIKE_REF_WORDS, geon=WHERE_NOT_LIKE_GEONAMES,
            lm=max(limit_N) if not SAMPLE_MAX_SIZE else str(int(SAMPLE_MAX_SIZE/4)) \
                if limit_N[2] == int(SAMPLE_MAX_SIZE/4) else \
                int(SAMPLE_MAX_SIZE/4) + (int(SAMPLE_MAX_SIZE/4) - limit_N[2])
        ))
        
        ROW_COUNT['N_ROW_NOT_LIKE'] = row_num(CON_PGSQL, non_ref)
        
        TMP_TABLES.append(non_ref)
    
    SAMPLE_TBL = tbls_to_tbl(CON_PGSQL, TMP_TABLES, 'sss_full')
    TMP_TABLES.append(SAMPLE_TBL)
    
    # Export data
    
    DATA_SCHEMA["OTHER_COLS"].append(DATA_SCHEMA["FID"])
    
    dataDf = q_to_obj(
        CON_PGSQL, "SELECT * FROM {}".format(SAMPLE_TBL)
    )
    
    dfParts = split_df_inN(dataDf, SPLIT_IN) if SPLIT_IN > 1 else [dataDf]
    
    obj_to_tbl(
        dfParts, OUTFILE,
        sheetsName=["sample_{}".format(i) for i in range(len(dfParts))])
    
    del_tables(CON_PGSQL, TMP_TABLES)
    
    # Write meta
    with open(os.path.join(
        os.path.dirname(OUTFILE),
        os.path.splitext(os.path.basename(OUTFILE))[0]) + '.txt', 'w') as txt:
        for k in ROW_COUNT:
            txt.write('{} -> {}\n'.format(k, ROW_COUNT[k]))


"""
Script Initialization
"""

if __name__ == "__main__":
    args = arg_parsing()
    
    conPG = {
        'HOST'     : 'localhost', 'USER' : 'postgres',
        'PASSWORD' : 'admin', 'PORT' : '5432', "DATABASE" : "expvgim_db"
    }
    
    WORD_SCHEMA = {
        "TNAME"      : "geotmlnh_words",
        "WORD"       : "word",
        "GRP_FK"     : "grp_id",
        "TGROUP"     : "geotmlnh_wordgrp",
        "GRP_FID"    : "fid",
        "GROUP"      : "desc",
        "GRP_FILTER" : "fire"
    }

    DATA_SCHEMA = {
        "TNAME"      : (
            "("
            "SELECT post_id, "
            "CASE WHEN type = 'link' THEN description ELSE message END AS message, "
            "type, link, datahora, page_ref FROM geotmlnh_facedata"
            ") AS foo"
        ),
        "FID"        : "post_id",
        "TEXT_COL"   : "message",
        "TIME"       : "datahora",
        "OTHER_COLS" : ["type", "page_ref"],
        "LOWER_TIME" : "2018-12-31 23:59:59",
        "HIGH_TIME"  : "2019-10-01 23:59:59",
        "PAGE_REF"   : "page_ref"
    }
    
    FACE_PAGES = [
        'diariocoimbra', 'diarioasbeiras', 'diariodeNoticias.pt',
        'cmjornal', 'jornalsol', 'rtpnoticias', 'sicnoticias',
        'Publico', 'NoticiasAoMinuto', 'jornalexpresso',
        'ionline.jornal', 'noticiasdecoimbra', 'tvi24',
        '24sapo', 'diarioleiria', 'jornalnoticias',
        'ObservadorOnTime', 'diarionoticias', 'diarioleiria',
        'jornaldamealhada', 'jornalterrasdesico',
        'jornaldabatalha', 'regiaodeleiria', 'diarioaveiro',
        'leiriatv', 'ojornaldeleiria'
    ]

    SPLIT_IN = 2

    SAMPLE_MAX_SIZE = 10000
    
    GN = {"TNAME" : "geotmlnh_geonames", "GEONAME" : "geoname"}
    
    get_sample(conPG, WORD_SCHEMA, DATA_SCHEMA, args.path_out_file,
               FACE_PAGES=FACE_PAGES, SPLIT_IN=SPLIT_IN, GEONAME_SCHEMA=GN,
               SAMPLE_MAX_SIZE=SAMPLE_MAX_SIZE)