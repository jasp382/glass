"""
Undersee IN SITU Observations to SRM Files and NetCDF Files

Execution instructions:
1 - Produce a SRM file for a specific day:

python db_to_txt_nc.py /home/user/folder --day 2019-09-20 --user diaryobs

2 - Produce a netCDF4 file for a specific day:

python db_to_txt_nc.py /home/user/folder --netcdf --day 2019-09-20 --user diaryobs

3 - Produce a netCDF file for every day in a range

python db_to_txt_nc.py /home/user/folder --netcdf --user diaryobs \
    --firstday 2019-12-09 --lastday 2019-12-18

python obs_to_txt_nc.py /mnt/d/gpto/undersee/ --user diaryobs --position_quality 0 \
    --default_longitude -9.144344 --default_latitude 38.696150\
    --netcdf --firstday 2019-12-26 2020-02-12
"""

# Python Packages
import os
import argparse
import datetime as dt
import json

"""
Script Arguments
"""
def args_parse():
    p = argparse.ArgumentParser(
        description="Undersee database content to files"
    )
    
    p.add_argument(
        'outpath', help="Path to the output file"
    )
    
    p.add_argument(
        '-nc', '--netcdf', action='store_true',
        help="Use this flag to produce a netCDF4 file"
    )
    
    p.add_argument(
        '-d', '--day', default=None,
        help="Day in the YYYY-MM-DD format"
    )
    
    p.add_argument(
        '-fd', '--firstday', default=None,
        help="First Day in the YYYY-MM-DD format"
    )
    
    p.add_argument(
        '-ld', '--lastday', default=None,
        help="Last Day in the YYYY-MM-DD format"
    )
    
    p.add_argument(
        '-u', '--user', default=None,
        help="Username of FTP user"
    )

    p.add_argument(
        '-p', '--position_quality', default=1, type=int,
        help="Position quality: 1 means Good Quality; 0 means Bad Quality"
    )

    p.add_argument(
        '-lt', '--default_latitude', default=0, type=float,
        help="Latitude value to apply when position_quality is 0"
    )

    p.add_argument(
        '-lg', '--default_longitude', default=0, type=float,
        help="Longitude value to apply when position_quality is 0"
    )
    
    return p.parse_args()


###############################################################################
############################# Auxilary methods ################################
###############################################################################

def quality_assessment(df, tempCol, timeCol):
    """
    Apply the following rules to get a quality flag:
    
    1 - The first 130 values of the day have poor quality;
    2 - For two sequential measures, if delta time > 1h AND delta temperature
        > 1C, the next 130 measures have poor quality;
    3 - For two sequential measures, if delta time > 1min AND delta temperature
        > 0.3C, the next 20 measures have poor quality.
    """
    
    import numpy as np
    
    # Produce observations FID
    df['myidx'] = df.index + 1
    
    # Comparing row values with previous row values
    jdf = df.copy()
    
    jdf['myidx'] = jdf.myidx + 1
    jdf.rename(columns={
        tempCol : 'lagtemp', timeCol : 'lagtime', 'myidx' : 'jidx'
    }, inplace=True)
    jdf.drop([c for c in jdf.columns.values if c != 'lagtime' \
              and c != 'lagtemp' and c != 'jidx'], axis=1, inplace=True)
    
    df = df.merge(jdf, how='left', left_on='myidx', right_on='jidx')
    df['dtime'] = df[timeCol] - df.lagtime
    df['dtime'] = df.dtime.dt.total_seconds()
    df['dtemp'] = df.lagtemp - df[tempCol]
    df['dtemp'] = df.dtemp.abs()
    
    # Apply rules
    df['rule1'] = np.where(df.myidx <= 130, 1, 0)
    
    df['rule2'] = np.where(
        (df.dtemp > 1) & (df.dtime > 3600) & (df.rule1 == 0),
        1, 0
    )
    badQR = df[df.rule2 == 1].myidx.tolist()
    badQR = [(i, i+130) for i in badQR]
    for i in badQR:
        df['rule2'] = np.where(
            (df.myidx >= i[0]) & (df.myidx < i[1]), 1, df.rule2
        )
    
    df['rule3'] = np.where(
        ((df.dtemp > 0.3) | (df.dtime > 60)) & (df.rule1 == 0), 1, 0
    )
    badQR = df[df.rule3 == 1].myidx.tolist()
    badQR = [(i, i+20) for i in badQR]
    for i in badQR:
        df['rule3'] = np.where(
            (df.myidx >= i[0]) & (df.myidx < i[1]), 1, df.rule3
        )
    
    # Set Quality Flag
    # 1 - Good Quality; 4 - Bad quality
    df['quality'] = np.where(
        (df.rule1 == 0) & (df.rule2 == 0) & (df.rule3 == 0), 1, 4
    )
    
    # Delete uncessary columns
    df.drop(['jidx', 'myidx', 'lagtemp', 'lagtime', 'dtime',
             'dtemp', 'rule1', 'rule2', 'rule3'], axis=1, inplace=True)
    
    return df


def txt_nodata(day, out):
    """
    There is no data for a specific day. Write txt file saying that. 
    """
    
    import codecs
    
    outTxt = os.path.splitext(out)[0] + '.txt'
    with codecs.open(outTxt, 'w', encoding='utf-8') as f:
        f.write('No Data was collected in {}'.format(day))
    
    return out

###############################################################################
###############################################################################
"""
Conversion Methods
"""
def db_to_srm(db, TABLE, TIME, TEMP, DAY, COLS_ORDER, COL_MAP, OUT_SRM,
              macs=None, deflong=None, deflat=None):
    """
    Database to SRM
    
    TODO: depth is not in the database, how to solve the issue
    """
    
    import codecs
    from glass.sql.fm   import q_to_obj
    from glass.gt.toshp import df_to_shp
    
    # Get Data from the Database
    q = (
        "SELECT {cols}, {t}.{tmCol} AS daytime{dep} "
        "FROM {t} {lf}WHERE {_mac}"
        "{t}.{tmCol} >= TIMESTAMP('{d} 00:00:00') "
        "AND {t}.{tmCol} <= TIMESTAMP('{d} 23:59:59') "
        "ORDER BY {t}.{tmCol}"
    ).format(
        t=TABLE, d=DAY, tmCol=TIME,
        cols=", ".join(["{t}.{_c} AS {_c}".format(
            t=TABLE, _c=c) for c in COLS_ORDER]),
        dep="" if 'depth' not in COL_MAP else ", 1 AS depth",
        lf="" if not macs else (
            "LEFT JOIN products AS jtbl "
            "ON {}.product_id = jtbl.id ").format(TABLE),
        _mac="" if not macs else "({}) AND ".format(
            " OR ".join(["jtbl.mac='{}'".format(m) for m in macs])
        )
    )
    df = q_to_obj(db, q, db_api='mysql')
    
    if not df.shape[0]:
        return txt_nodata(DAY, OUT_SRM)
    
    if deflong and deflat:
        latcol=None; lngcol=None
        for k in cols_map:
            if cols_map[k] == 'latitude':
                latcol = k
            
            elif cols_map[k] == 'longitude':
                lngcol = k
            
            if latcol and lngcol:
                break
        
        df[lngcol] = deflong
        df[latcol] = deflat
    
    # Apply quality assessment
    df = quality_assessment(df, TEMP, 'daytime')
    df = df[df.quality == 1]
    
    df.reset_index(inplace=True)
    
    if not df.shape[0]:
        return txt_nodata(DAY, OUT_SRM)
    
    cols_order = COLS_ORDER.copy()
    if 'depth' in COL_MAP:
        cols_order.insert(2, 'depth')
    
    """
    Calculate time differences between the time of each row
    and the time of the first row
    """
    df['idx'] = df.index + 1
    
    lagDf = df.copy()
    lagDf['lag_idx'] = df.idx + 1
    lagDf.drop(['idx'] + list(COL_MAP.keys()), axis=1, inplace=True)
    lagDf.rename(columns={'daytime' : 'lagtime'}, inplace=True)
    
    df = df.merge(lagDf, how='left', left_on="idx", right_on='lag_idx')
    df['seconds'] = df.daytime - df.lagtime
    df['seconds'] = df.seconds.dt.total_seconds()
    df['seconds'] = df.seconds.fillna(0)
    df['cumseconds'] = df.seconds.cumsum()
    df.seconds = df.seconds.astype(int)
    df.cumseconds = df.cumseconds.astype(int)
    
    """
    Write Output File
    """
    initialTime = df.loc[0, 'daytime']
    with codecs.open(OUT_SRM, 'w', encoding='utf-8') as txt:
        txt.write("Time Serie Results File\n")
        txt.write((
            " SERIE_INITIAL_DATA      : {}.  {}. {}.  {}.  {}.  {}.\n"
        ).format(
            str(initialTime.year), str(initialTime.month),
            str(initialTime.day), str(initialTime.hour),
            str(initialTime.minute), str(initialTime.second)
        ))
        
        txt.write("TIME_UNITS              : SECONDS\n")
        
        txt.write("Seconds       {}\n".format(
            "   ".join([COL_MAP[c] for c in cols_order])
        ))
        
        txt.write("<BeginTimeSerie>\n")
        
        # Write Rows
        df['txt'] = df.cumseconds.astype(str)
        for c in cols_order:
            df['txt'] = df.txt + "   " + df[c].astype(str)
        
        txt.write(df.txt.str.cat(sep="\n"))
            
        txt.write("\n<EndTimeSerie>")
    
    return OUT_SRM


def db_to_nc_v2(db, tbl, daystr, _dimCols, _varCols, tempCol, timeCol, outNc,
                pos_quality_flag, deflong=None, deflat=None, macs=None):
    """
    DB to NC according Copernicus specifications for data collected IN SITU
    """
    
    import netCDF4
    import numpy as np
    from glass.sql.fm import q_to_obj
    
    dimCols = _dimCols.copy()
    varCols = _varCols.copy()
    
    ############################################################################
    ########################## Global Variables ################################
    QCF = "quality flag"
    CT2 = "OceanSITES reference table 2"
    QFlags = np.array([0,1,2,3,4,5,6,7,8,9]).astype('int8')
    QC_STR = (
        "no_qc_performed good_data probably_good_data "
        "bad_data_that_are_potentially_correctable bad_data "
        "value_changed not_used nominal_value "
        "interpolated_value missing_value"
    )
    
    DM = 'method of data processing'
    DMC = 'OceanSITES reference table 5'
    DMFlag = "R, P, D, M"
    DMMean = 'real-time provisional delayed-mode mixed'
    ############################################################################
    """
    Get Data From Database
    """
    Q = (
        "SELECT {dim}, {var} FROM {t} {lf}"
        "WHERE {_mac}{t}.{tmCol} >= TIMESTAMP('{d} 00:00:00') AND "
        "{t}.{tmCol} <= TIMESTAMP('{d} 23:59:59') "
        "ORDER BY {t}.{tmCol}"
    ).format(
        dim=", ".join(["{} AS {}".format(
            d["DB_COL"], d["SLUG"]) for d in dimCols]),
        var=", ".join(["{} AS {}".format(
            v["DB_COL"], v["SLUG"]) for v in varCols]),
        t=tbl, d=daystr, tmCol=timeCol,
        lf="" if not macs else (
            "LEFT JOIN products AS jtbl "
            "ON {}.product_id = jtbl.id "
        ).format(tbl),
        _mac="" if not macs else "({}) AND ".format(
            " OR ".join(["jtbl.mac='{}'".format(m) for m in macs])
        )
    )
    geoDf = q_to_obj(db, Q, db_api='mysql')
    
    if not geoDf.shape[0]:
        return txt_nodata(daystr, outNc)
    
    # Get Quality Flag for observations in File
    temperatureCol = None
    timeDim        = None
    for i in dimCols:
        if i['DB_COL'] == "{}.{}".format(tbl, timeCol):
            timeDim = i["SLUG"]
        else:
            continue
    for i in varCols:
        if i['DB_COL'] == "{}.{}".format(tbl, tempCol):
            temperatureCol = i["SLUG"]
        else: continue
    geoDf = quality_assessment(geoDf, temperatureCol, timeDim)
    geoDf = geoDf[geoDf.quality == 1]
    
    geoDf.reset_index(inplace=True)
    
    if not geoDf.shape[0]:
        return txt_nodata(daystr, outNc)
    
    # Get Dimensions X and Y
    for i in dimCols:
        if i["AXIS"] == 'X':
            lngDim = i["SLUG"]
        elif i["AXIS"] == 'Y':
            latDim = i["SLUG"]
    
    """ Create NC File """
    ncObj = netCDF4.Dataset(outNc, 'w', clobber=True)
    
    """ Add Global Attributes """
    ncObj.data_type = " "
    ncObj.format_version = " "
    ncObj.plaform_code = "TTDAFUNDO"
    ncObj.data_mode = "R"
    ncObj.id = os.path.splitext(os.path.basename(outNc))[0]
    ncObj.geospatial_lat_min = str(geoDf[latDim].min())
    ncObj.geospatial_lat_max = str(geoDf[latDim].max())
    ncObj.geospatial_lon_min = str(geoDf[lngDim].min())
    ncObj.geospatial_lon_max = str(geoDf[lngDim].max())
    ncObj.geospatial_vertical_min = "1"
    ncObj.geospatial_vertical_max = "1"
    ncObj.time_coverage_start = str(geoDf[timeDim].min())
    ncObj.time_coverage_end   = str(geoDf[timeDim].max())
    
    """ Create Default Dimensions """
    ncObj.createDimension("POSITION", geoDf.shape[0])
    ncObj.createDimension("STRING32", 32)
    ncObj.createDimension("STRING256", 256)
    
    """ Create User Dimensions and Related Variables """
    for d in dimCols:
        # Create Dimension
        if d["AXIS"] == 'T':
            varValues = None
            ncObj.createDimension(d["SLUG"], None)
        else:
            if d["AXIS"] == 'X' or d["AXIS"] == 'Y':
                if not pos_quality_flag and d["AXIS"] == 'X' and deflong:
                    varValues = np.full(geoDf.shape[0], deflong)
                elif not pos_quality_flag and d["AXIS"] == 'Y' and deflat:
                    varValues = np.full(geoDf.shape[0], deflat)
                else:
                    varValues = geoDf[d["SLUG"]]
            else:
                varValues = geoDf[d["SLUG"]].unique()
            ncObj.createDimension(d["SLUG"], varValues.shape[0])
        
        # Create Variable
        d["VAROBJ"] = ncObj.createVariable(
            d["SLUG"], d["TYPE"],
            (d["SLUG"]) if 'IS_CHILD' not in d else d["IS_CHILD"],
            fill_value=d["FILL"]
        )
        
        # Add Attributes to Variable
        d["VAROBJ"].units         = d["UNIT"]
        d["VAROBJ"].long_name     = d["LONG_NAME"]
        d["VAROBJ"].standard_name = d["STANDARD_NAME"]
        d["VAROBJ"].axis          = d["AXIS"]
        d["VAROBJ"].valid_min     = d["MIN"]
        d["VAROBJ"].valid_max     = d["MAX"]
        
        # Set Variable Values
        if d["AXIS"] != 'T' and d["AXIS"] != 'Z':
            d["VAROBJ"][:] = varValues.tolist()
        
        # Add variable for Quality Flag
        if d["AXIS"] == 'T' or d["AXIS"] == 'Z':
            d["QC"] = ncObj.createVariable(
                d["SLUG"] + "_QC", 'byte',
                (d["SLUG"]) if 'IS_CHILD' not in d else d["IS_CHILD"],
                fill_value=-128
            )
            
            d["QC"].long_name    = QCF
            d["QC"].conventions  = CT2
            d["QC"].valid_min    = 0
            d["QC"].valid_max    = 9
            d["QC"].flag_values  = QFlags
            d["QC"].flag_meanings = QC_STR
            
            d["QC"][:] = np.full(geoDf.shape[0], 1) if 'IS_CHILD' not in d else \
                np.full((geoDf.shape[0], 1), 1)
        
        # Add variable for Data processing method
        if d["AXIS"] == 'Z':
            d["DM"] = ncObj.createVariable(
                d["SLUG"] + "_DM", "S1",
                (timeDim, d["SLUG"]), fill_value= " "
            )
            
            d["DM"].long_name     = DM
            d["DM"].conventions   = DMC
            d["DM"].flag_values   = DMFlag
            d["DM"].flag_meanings = DMMean
    
    """ Create Data Variables """
    for v in varCols:
        v["VAROBJ"] = ncObj.createVariable(
            v["SLUG"], v["TYPE"], v["DIM"], zlib=True, fill_value=-9999
        )
        
        v["VAROBJ"].units         = v["UNIT"]
        v["VAROBJ"].long_name     = v["LONG_NAME"]
        v["VAROBJ"].standard_name = v["STANDARD_NAME"]
        
        # Create DM Var
        v["DM"] = ncObj.createVariable(
            v["SLUG"] + "_DM", "S1", v["DIM"], fill_value=" "
        )
        
        v["DM"].long_name     = DM
        v["DM"].conventions   = DMC
        v["DM"].flag_values   = DMFlag
        v["DM"].flag_meanings = DMMean
        
        # Create QC car
        v["QC"] = ncObj.createVariable(
            v["SLUG"] + "_QC", "byte", v["DIM"], fill_value=-128)
        
        v["QC"].long_name = QCF
        v["QC"].conventions  = CT2
        v["QC"].valid_min    = 0
        v["QC"].valid_max    = 9
        v["QC"].flag_values  = QFlags
        v["QC"].flag_meanings = QC_STR
    
    """ Create other meta variables """
    # Position QC
    pqc = ncObj.createVariable('POSITION_QC', "byte", ("POSITION"))
    pqc.long_name = QCF
    pqc.conventions = CT2
    pqc.valid_min = 0
    pqc.valid_max = 9
    pqc.flag_values = QFlags
    pqc.flag_meanings = QC_STR
    pqc[:] = np.full(geoDf.shape[0], 1 if pos_quality_flag != 0 else 9)
    
    # Create DC Reference
    dcref = ncObj.createVariable('DC_REFERENCE', 'S1', (timeDim, "STRING32"))
    dcref.long_name = "Station/Location unique identifier in data centre"
    dcref.conventions = "Data centre convention"
    
    # Create POSITION SYSTEM
    pos_sys = ncObj.createVariable('POSITIONING_SYSTEM', 'S1', ("POSITION"))
    pos_sys.long_name = "Positioning system"
    pos_sys.flag_values = "A, G, L, N, U"
    pos_sys.flag_meanings = "Argos, GPS, Loran, Nominal, Unknown"
    pos_sys[:] = ['G' for i in range(geoDf.shape[0])]
    
    """ Add data to Variables """
    year, month, day = daystr.split('-')
    basedate = dt.datetime(1950,1,1,0,0,0)
    
    for d in dimCols:
        if d["SLUG"] != timeDim:
            continue
        else:
            timeDimObj = d
            break
    
    i = 0
    for idx, row in geoDf.iterrows():
        tempo = row[timeDim]
        date = dt.datetime(
            int(tempo.year), int(tempo.month), int(tempo.day),
            int(tempo.hour), int(tempo.minute), int(tempo.second)
        )
        dtime = (date - basedate).total_seconds()/86400
        timeDimObj["VAROBJ"][i] = dtime
        
        for d in dimCols:
            if d["AXIS"] == 'Z':
                d["VAROBJ"][i, :] = [row[d["SLUG"]]]
                break
            else:
                continue
        
        for v in varCols:
            v["VAROBJ"][i, :] = [row[v["SLUG"]]]
            v["QC"][i, :] = row.quality
        i+=1
    
    """ Close File """
    ncObj.close()
    
    return outNc


###############################################################################
###############################################################################
"""
Run Script
"""
if __name__ == '__main__':
    """
    Get user Arguments
    """
    
    ARGS = args_parse()
    
    """
    Parameters to connect to Database
    """
    
    thisFile = os.path.abspath(__file__)
    glb_var = json.load(open(os.path.join(
        os.path.dirname(thisFile),
        os.path.splitext(os.path.basename(thisFile))[0]+ '.json'
    ), 'r'))
    
    # Database Meta
    con_db     = glb_var["DBCON"]
    data_table = glb_var["DATA_TABLE"]
    time_col   = glb_var["TIME_COL"]
    temp_col   = glb_var["TEMP_COL"]
    
    """ Processing Day or Days """
    if ARGS.firstday and ARGS.lastday:
        from glass.pyt.tm import timerange
        
        day = timerange(ARGS.firstday, ARGS.lastday)
    
    elif not ARGS.firstday and ARGS.lastday:
        day = [ARGS.lastday]
    
    elif ARGS.firstday and not ARGS.lastday:
        # Create time range from firstday to yesterday
        from glass.pyt.tm import timerange

        day = timerange(ARGS.firstday, str(
            dt.datetime.now().replace(
                microsecond=0).date() - dt.timedelta(days=1)
        ))
    
    else:
        day = [str(dt.datetime.now().replace(
            microsecond=0).date() - dt.timedelta(
                days=1))] if not ARGS.day else [ARGS.day]
    
    """ User Macs """
    USERS = glb_var["USERS"]
    MACS = None if not ARGS.user else USERS[ARGS.user] if \
        ARGS.user in USERS else None
    
    """ Ouput Path """
    BASE_FOLDER = ARGS.outpath
    
    file_b = "IR_TS_FB_TTDAFUNDO"
    out_file = [os.path.join(
        BASE_FOLDER, "{}_{}.{}".format(
            file_b, d.replace('-', ''),
            'nc' if ARGS.netcdf else 'srm'
        )
    ) for d in day]
    
    if not ARGS.netcdf:
        """
        Produce SRM File
        """
        cols_order = [
            'value19', 'value18', 'value1', 'value4',
            'value2', 'value8', 'value6', 'value15', 'value16'
        ]; cols_map   = {
            'value1'  : 'temperature(C)',
            'value18' : 'latitude',
            'value19' : 'longitude',
            'value4'  : 'practical_salinity(psu)',
            'depth'   : 'depth(m)',
            'value2'  : 'electrical_conductivity(Sm-1)',
            'value8'  : 'dissolved_oxygen(mg_l-1)',
            'value6'  : 'ph',
            'value15' : 'chla_fluorescence(mg_m-3)',
            'value16' : 'turbidity'
        }
        
        # Produce file or files
        for i in range(len(day)):
            db_to_srm(
                con_db, data_table, time_col, temp_col, day[i],
                cols_order, cols_map, out_file[i], macs=MACS,
                deflong=None if not ARGS.default_longitude else ARGS.default_longitude,
                deflat=None if not ARGS.default_latitude else ARGS.default_latitude
            )
    
    else:
        """
        Produce netCDF4 file according Copernicus specification
        """
        
        dimensionCols = [
            {
                "DB_COL" : '{}.value18'.format(data_table),
                "STANDARD_NAME" : 'latitude',
                "LONG_NAME" : 'Latitude of each location',
                "UNIT" : "degree_north",
                "AXIS" : "Y", "SLUG" : "LATITUDE",
                "MIN" : -90.0, "MAX" : 90.0,
                "TYPE" : 'f4', "FILL" : 99999.0
            },{
                "DB_COL" : '{}.value19'.format(data_table),
                "STANDARD_NAME" : 'longitude',
                "LONG_NAME" : 'Longitude of each location',
                "UNIT" : 'degree_east', "SLUG" : "LONGITUDE",
                "AXIS" : "X", "MIN" : -180.0, "MAX" : 180.0,
                "TYPE" : 'f4', "FILL" : 99999.0
            }, {
                "DB_COL" : '{}.created_at'.format(data_table),
                "STANDARD_NAME" : 'time',
                "LONG_NAME" : 'Time', "SLUG" : "TIME",
                "UNIT" : "days since 1950-01-01T00:00:00Z",
                "MIN" : -90000.0, "MAX" : 90000.0,
                "AXIS" : 'T', "TYPE" : 'd', "FILL" : 999999.0
            }, {
                "DB_COL" : '1',
                "STANDARD_NAME" : 'depth',
                "LONG_NAME" : 'Depth', 'UNIT' : 'm',
                "SLUG" : 'DEPH', "AXIS" : "Z",
                "MIN" : -12000.0, "MAX" : 12000,
                "TYPE" : 'i4', "IS_CHILD" : ("TIME", "DEPH"),
                "FILL" : -99999.0
            }
        ]
        
        variableCols = [
            {
                "DB_COL" : '{}.value1'.format(data_table),
                "STANDARD_NAME" : 'sea_water_temperature', 
                "LONG_NAME" : 'Sea temperature', 
                "UNIT" : 'degrees_C', 'SLUG': 'TEMP',
                "TYPE" : 'f4',
                "DIM" : ("TIME", "DEPH")
            }, {
                "DB_COL" : '({}.value2 / 10000.0)'.format(data_table),
                "STANDARD_NAME" : 'sea_water_electrical_conductivity',
                "LONG_NAME" : 'Electrical conductivity',
                "UNIT" : 'S m-1', "SLUG" : "CNDC",
                "TYPE" : 'f4', "DIM" : ("TIME", "DEPH")
            }, {
                "DB_COL" : '{}.value4'.format(data_table),
                "STANDARD_NAME" : 'sea_water_practical_salinity', 
                "LONG_NAME" : 'Practical salinity', 
                "UNIT" : '0.001', 'SLUG' : 'PSAL',
                "TYPE" : 'f4', "DIM" : ("TIME", "DEPH")
            }, {
                "DB_COL" : '({}.value8 / 1.33)'.format(data_table),
                "STANDARD_NAME" : 'volume_fraction_of_oxygen_in_sea_water',
                "LONG_NAME" : 'Dissolved oxygen',
                "UNIT" : 'ml l-1', 'SLUG' : 'DOX1',
                "TYPE" : "f4", "DIM" : ("TIME", "DEPH")
            }, {
                "DB_COL" : '{}.value6'.format(data_table),
                "STANDARD_NAME" : 'sea_water_ph_reported_on_total_scale',
                "LONG_NAME" : 'Ph', "UNIT" : "1", "SLUG" : 'PHPH',
                "TYPE" : "f4", "DIM" : ("TIME", "DEPH")
            }, {
                "DB_COL" : '{}.value15'.format(data_table),
                "STANDARD_NAME" : 'mass_concentration_of_chlorophyll_a_fluorescence_in_sea_water',
                "LONG_NAME" : 'Chlorophyll-a fluorescence',
                "UNIT" : 'mg m-3', "SLUG" : "FLU2",
                "TYPE" : "f4", "DIM" : ("TIME", "DEPH")
            }, {
                "DB_COL" : '{}.value16'.format(data_table),
                "STANDARD_NAME" : 'sea_water_turbidity',
                "LONG_NAME" : 'Turbidity',
                "UNIT" : '1', "SLUG" : "TUR4",
                "TYPE" : "f4", "DIM" : ("TIME", "DEPH")
            }
        ]

        POSITION_QFLAG = 1 if ARGS.position_quality != 0 else 0
        DEFAULT_LAT = None if not ARGS.default_latitude else \
            ARGS.default_latitude
        DEFAULT_LNG = None if not ARGS.default_longitude else \
            ARGS.default_longitude 
        
        for i in range(len(day)):
            db_to_nc_v2(
                con_db, data_table, day[i], dimensionCols, variableCols,
                temp_col, time_col, out_file[i], POSITION_QFLAG,
                deflong=DEFAULT_LNG, deflat=DEFAULT_LAT, macs=MACS)
