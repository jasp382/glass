"""
Group data into classes
"""


def datatocls_meanstd(shp_data, maps_table, sheet, slug, title,
    ncls, decplace, nodata, out_shp, out_maps_tbl, grpcol=None):
    """
    Create classes based on mean and standard deviation

    decplace - Numero casas decimais que vao aparecer nos valores do layout
    nodata - Must be always smaller than the min of min values
    """

    import pandas            as pd
    import numpy             as np
    from glass.rd.shp      import shp_to_obj
    from glass.wt.shp      import df_to_shp
    from glass.rd         import tbl_to_obj
    from glass.wt         import obj_to_tbl
    from glass.pd.fld     import listval_to_newcols
    from glass.lyt.diutils import eval_intervals

    # Read data
    shp_df = shp_to_obj(shp_data)

    maps_df = tbl_to_obj(maps_table, sheet=sheet)

    if grpcol:
        maps_cols = maps_df[slug].tolist()
        for c in maps_cols:
            shp_df[c] = shp_df[c].astype(float)
        agg_dict = {c : 'mean' for c in maps_cols}
        shp_df = pd.DataFrame(shp_df.groupby([grpcol]).agg(
            agg_dict
        )).reset_index()
    
    def get_intervals(_ncls, mean, std):
        mean_class = mean + (std / 2)
    
        less_mean = []
        major_mean = []
        for e in range(_ncls):
            if not e:
                less_mean.append(mean - (std / 2))
                major_mean.append(mean_class + std)
            else:
                less_mean.append(less_mean[e - 1] - std)
                major_mean.append(major_mean[e - 1] + std)
        
        less_mean.reverse()
        intervals = less_mean + [mean_class] + major_mean
    
        return intervals
    
    # Calculo intervalos para cada indicador
    # metodo intervalos baseados na media e no desvio padrao

    # Get min, max, mean and standard deviation
    # Round values
    i_stats = []
    for idx, row in maps_df.iterrows():
        ddig = row[decplace]
        i    = row[slug]
        t    = row[title]

        if nodata in shp_df[i].unique():
            vals = list(shp_df[i].unique())
            vals.sort()

            min_v = vals[1]
        
            tdf = shp_df[[i]].copy()
        
            tdf = tdf[tdf[i] >= min_v]
            tdf.reset_index(drop=True, inplace=True)
        
            max_v = tdf[i].max()
            mean_v = tdf[i].mean()
            std_v = tdf[i].std()
        
        else:
            min_v  = shp_df[i].min()
            max_v  = shp_df[i].max()
            mean_v = shp_df[i].mean()
            std_v  = shp_df[i].std()
        
        fbreak = min_v - 1
        __std = std_v
        while fbreak <= min_v:
            intervals = get_intervals(ncls, mean_v, __std)

            repeat = 0
            for __i in intervals[:-1]:
                if __i > max_v:
                    repeat = 1
                
                if repeat:
                    break
            
            fbreak = intervals[0] if not repeat else min_v - 1
            __std = __std / 2
        
        intervals[-1] = max_v

        if not str(shp_df[i].dtype).startswith('int'):
            __intervals = [round(_i, ddig) for _i in intervals]
        
            repeat = 1
            __intervals, ndig = eval_intervals(
                intervals, __intervals, ddig,
                round(min_v, ddig)
            )
        
            i_stats.append([
                i, t, round(min_v, ndig), round(max_v, ndig),
                round(mean_v, ddig), round(std_v, ddig), __intervals
            ])
        
            shp_df[i] = shp_df[i].round(ddig)
        
        else:
            for _e in range(len(intervals)):
                if not _e:
                    rzero = 1 if round(intervals[_e], 0) > min_v else 0
                
                else:
                    rzero = 1 if round(intervals[_e], 0) > \
                        round(intervals[_e - 1], 0) else 0
            
                if not rzero:
                    break
            
            __intervals = [round(_o, ddig if not rzero else 0) for _o in intervals]

            __intervals, ndig = eval_intervals(intervals, __intervals, ddig, min_v)

            i_stats.append([
                i, t, min_v, max_v,
                int(round(mean_v, 0)) if rzero else round(mean_v, ddig),
                int(round(std_v, 0)) if rzero else round(std_v, ddig),
                __intervals
            ])
    
    i_stats = pd.DataFrame(i_stats, columns=[
        'slug', 'title', 'min_value', 'max_value',
        'mean_value', 'std_value', 'intervals'
    ])

    rename_cols = {}
    for idx, row in i_stats.iterrows():
        # Get intervals.
        int_ = row.intervals
    
        # Add columns for intervals
        i_col = 'i_' + row.slug
        shp_df[i_col] = 0
    
        for _i in range(len(int_)):
            if not _i:
                shp_df[i_col] = np.where(
                    (shp_df[row.slug] > nodata) & (shp_df[row.slug] <= int_[_i]),
                    _i + 1, shp_df[i_col]
                )
            else:
                shp_df[i_col] = np.where(
                    (shp_df[row.slug] > int_[_i - 1]) & (shp_df[row.slug] <= int_[_i]),
                    _i + 1, shp_df[i_col]
                )
    
        rename_cols[i_col] = row.slug
    
    shp_df.drop(i_stats.slug, axis=1, inplace=True)
    shp_df.rename(columns=rename_cols, inplace=True)

    i_stats = listval_to_newcols(i_stats, 'intervals')

    i_stats.rename(columns={
        i : 'interval_' + str(i+1) for i in range((ncls * 2) + 1)
    }, inplace=True)

    if grpcol:
        nshp_df = shp_to_obj(shp_data)

        nshp_df.drop(maps_cols, axis=1, inplace=True)

        shp_df.rename(columns={grpcol : grpcol + '_y'}, inplace=True)

        shp_df = nshp_df.merge(shp_df, how='left', left_on=grpcol, right_on=grpcol + '_y')
    
    df_to_shp(shp_df, out_shp)

    obj_to_tbl(i_stats, out_maps_tbl)

    return out_shp, out_maps_tbl


def datatocls(shpfile, mapstbl, sheet, slug, title, ncls, decplace,
    outshp, outmapstbl, method="QUANTILE"):
    """
    Create classes/intervals for each map in table

    method options:
    * QUANTILE;
    * JENKS - natural breaks (jenks);
    """

    import pandas            as pd
    import numpy             as np
    from glass.rd.shp      import shp_to_obj
    from glass.wt.shp      import df_to_shp
    from glass.rd         import tbl_to_obj
    from glass.wt         import obj_to_tbl
    from glass.pd.fld     import listval_to_newcols
    from glass.lyt.diutils import eval_intervals

    methods = ["QUANTILE", "JENKS"]

    if method not in methods:
        raise ValueError(f'Method {method} is not available')

    if method == "QUANTILE":
        from glass.pd.stats import get_intervals
    
    elif method == "JENKS":
        import jenkspy

    # Read data
    shp  = shp_to_obj(shpfile)
    maps = tbl_to_obj(mapstbl, sheet=sheet)

    # Get intervals for each map
    istats = []
    for i, row in maps.iterrows():
        ddig = row[decplace]
        icol = row[slug]
        titl = row[title]
    
        min_v  = shp[icol].min()
        max_v  = shp[icol].max()
        mean_v = shp[icol].mean()
        std_v  = shp[icol].std()

        if method == "QUANTILE":
            intervals = get_intervals(shp, icol, ncls, method="QUANTILE")
            intervals.append(max_v)
        
        elif method == "JENKS":
            breaks = jenkspy.jenks_breaks(shp[icol], nb_class=ncls)
            intervals = breaks[1:]
        
        if not str(shp[icol].dtype).startswith('int'):
            __intervals = [round(i, ddig) for i in intervals]

            __intervals, ndig = eval_intervals(
                intervals, __intervals, ddig, round(min_v, ddig)
            )

            istats.append([
                icol, titl, round(min_v, ndig),
                round(max_v, ndig), round(mean_v, ddig),
                round(std_v, ddig), __intervals
            ])

            shp[icol] = shp[icol].round(ddig)
        
        else:
            for _e in range(len(intervals)):
                if not _e:
                    rzero = 1 if round(intervals[_e], 0) > min_v else 0
                
                else:
                    rzero = 1 if round(intervals[_e], 0) > \
                        round(intervals[_e - 1], 0) else 0
                
                if not rzero:
                    break
            
            __intervals = [round(
                _o, ddig if not rzero else 0
            ) for _o in intervals]

            __intervals, ndig = eval_intervals(
                intervals, __intervals, ddig, min_v)
            
            istats.append([
                icol, titl, min_v, max_v,
                int(round(mean_v, 0)) if rzero else round(mean_v, ddig),
                int(round(std_v, 0)) if rzero else round(std_v, ddig),
                __intervals
            ])
    
    istats = pd.DataFrame(istats, columns=[
        "slug", "title", "min_value", "max_value",
        "mean_value", "std_value", "intervals"
    ])

    rename_cols = {}
    for idx, row in istats.iterrows():
        # Get intervals
        int_ = row.intervals
    
        # Add columns for intervals
        i_col = 'i_' + row.slug
        shp[i_col] = 0
    
        for _i in range(len(int_)):
            if not _i:
                shp[i_col] = np.where(
                    shp[row.slug] <= int_[_i],
                    _i + 1, shp[i_col]
                )
        
            else:
                shp[i_col] = np.where(
                    (shp[row.slug] > int_[_i - 1]) & (shp[row.slug] <= int_[_i]),
                    _i + 1, shp[i_col]
                )
    
        rename_cols[i_col] = row.slug
    
    shp.drop(istats.slug, axis=1, inplace=True)
    shp.rename(columns=rename_cols, inplace=True)

    istats = listval_to_newcols(istats, 'intervals')

    istats.rename(columns={
        i : 'interval_' + str(i+1) for i in range(ncls)
    }, inplace=True)

    # Write outputs
    df_to_shp(shp, outshp)
    obj_to_tbl(istats, outmapstbl)

    return outshp, outmapstbl


def datatocls_multiref(shpfile, mapstbl, sheet, slugs, titles, ncls, decplace,
    outshp, outmapstbl, method="QUANTILE"):
    """
    Create classes/intervals for each layout in table (mapstbl)
    One layout could have more than one map... deal with that situation

    method options:
    * QUANTILE;
    * JENKS - natural breaks (jenks);
    """

    import pandas            as pd
    import numpy             as np
    from glass.pys           import obj_to_lst
    from glass.rd.shp      import shp_to_obj
    from glass.wt.shp      import df_to_shp
    from glass.rd         import tbl_to_obj
    from glass.wt         import obj_to_tbl
    from glass.pd.fld     import listval_to_newcols
    from glass.lyt.diutils import eval_intervals

    methods = ["QUANTILE", "JENKS"]

    if method not in methods:
        raise ValueError(f'Method {method} is not available')
    
    if method == "QUANTILE":
        from glass.pd.stats import get_intervals
    
    elif method == "JENKS":
        import jenkspy
    
    slugs  = obj_to_lst(slugs)
    titles = obj_to_lst(titles)
    
    # Read data
    shp  = shp_to_obj(shpfile)
    maps = tbl_to_obj(mapstbl, sheet=sheet)

    # Get intervals for each map
    istats = []
    cols   = []
    for i, row in maps.iterrows():
        ddig  = row[decplace]
        icols = [row[slug] for slug in slugs]
        ititles = [row[title] for title in titles]

        istatsrow = []
        for _i in range(len(icols)):
            min_v  = shp[icols[_i]].min()
            max_v  = shp[icols[_i]].max()
            mean_v = shp[icols[_i]].mean()
            std_v  = shp[icols[_i]].std()

            if method == "QUANTILE":
                intervals = get_intervals(
                    shp, icols[_i], ncls, method="QUANTILE")
                intervals.append(max_v)
            
            elif method == "JENKS":
                breaks = jenkspy.jenks_breaks(shp[icols[_i]], nb_class=ncls)
                intervals = breaks[1:]
            
            if not str(shp[icols[_i]].dtype).startswith('int'):
                __intervals = [round(itv, ddig) for itv in intervals]

                __intervals, ndig = eval_intervals(
                    intervals, __intervals, ddig, round(min_v, ddig)
                )

                istatsrow.extend([
                    icols[_i], ititles[_i], round(min_v, ndig),
                    round(max_v, ndig), round(mean_v, ddig),
                    round(std_v, ddig), __intervals
                ])

                shp[icols[_i]] = shp[icols[_i]].round(ddig)
            
            else:
                for _e in range(len(intervals)):
                    if not _e:
                        rzero = 1 if round(intervals[_e], 0) > min_v else 0
                    
                    else:
                        rzero = 1 if round(intervals[_e], 0) > \
                            round(intervals[_e -1], 0) else 0
                    
                    if not rzero:
                        break
                
                __intervals = [round(
                    _o, ddig if not rzero else 0
                ) for _o in intervals]

                __intervals, ndig = eval_intervals(
                    intervals, __intervals, ddig, min_v
                )

                istatsrow.extend([
                    icols[_i], ititles[_i], min_v, max_v,
                    int(round(mean_v, 0)) if rzero else round(mean_v, ddig),
                    int(round(std_v, 0)) if rzero else round(std_v, ddig),
                    __intervals
                ])
            
            if not i:
                cols.extend([
                    f'slug{str(_i+1)}', f'title{str(_i+1)}',
                    f'min_value{str(_i+1)}', f'max_value{str(_i+1)}',
                    f'mean_value{str(_i+1)}',
                    f'std_value{str(_i+1)}', f'intervals{str(_i+1)}'
                ])
        
        istats.append(istatsrow)
    
    istats = pd.DataFrame(istats, columns=cols)

    rename_cols = {}
    for idx, row in istats.iterrows():
        for _i in range(len(slugs)):
            # Get intervals
            int_ = row[f'intervals{str(_i+1)}']

            # Add columns for intervals ids
            newcol = 'i_' + row[f'slug{str(_i+1)}']
            shp[newcol] = 0

            for itv in range(len(int_)):
                if not itv:
                    shp[newcol] = np.where(
                        shp[row[f'slug{str(_i+1)}']] <= int_[itv],
                        itv + 1, shp[newcol]
                    )
                
                else:
                    shp[newcol] = np.where(
                        (shp[row[f'slug{str(_i+1)}']] > int_[itv-1]) & (shp[row[f'slug{str(_i+1)}']] <= int_[itv]),
                        itv + 1, shp[newcol]
                    )
            
            rename_cols[newcol] = row[f'slug{str(_i+1)}']
    
    dc = []
    for c in range(len(slugs)):
        dc.extend(istats[f'slug{str(c+1)}'].tolist())
    
    shp.drop(dc, axis=1, inplace=True)
    shp.rename(columns=rename_cols, inplace=True)

    
    for i in range(len(slugs)):
        istats = listval_to_newcols(istats, f'intervals{str(i+1)}')
        istats.rename(columns={
            ii : f'intervals{str(i+1)}_{str(ii+1)}' for ii in range(ncls)
        }, inplace=True)
    
    # Write outputs
    df_to_shp(shp, outshp)
    obj_to_tbl(istats, outmapstbl)

    return outshp, outmapstbl

