"""
Database SCHEMA
"""

FACEBOOK_SCHEMA = {
    'SAMPLE_T'     : 'geotmlnh_refdata',
    'SAMPLE_PK'    : 'fid',
    'SAMPLE_FK'    : 'postid',
    'DATA_T'       : 'geotmlnh_facedata',
    'DATA_ID'      : 'post_id',
    'TXT_COL'      : (
        "CASE WHEN geotmlnh_facedata.type = 'link' "
        "THEN geotmlnh_facedata.description "
        "ELSE geotmlnh_facedata.message END"
    ),
    'TIME_COL'     : 'datahora',
    'REF_COL'      : 'is_fire',
    'SAMPLE_TXT_T' : 'geotmlnh_refdatatxt',
    'SAMPLE_TXT_PK': 'fid',
    'SAMPLE_TXT_FK': 'rid'
}


REFDATA_SCHEMA = {
    'TABLE'         : 'geotmlnh_refdata',
    'PK'            : 'fid',
    'REF_COL'       : 'is_fire',
    'DATA_COL'      : 'txt_pp',
    'SAMPLE_TXT_T'  : 'geotmlnh_refdatatxt',
    'SAMPLE_TXT_PK' : 'fid',
    'SAMPLE_TXT_FK' : 'rid'
}