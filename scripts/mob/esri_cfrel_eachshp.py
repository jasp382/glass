"""
Run ESRI Closest Facilities based on relations for every 
ESRI Shapefile in a folder
"""

if __name__ == "__main__":
    import os
    from glass.pys.oss import lst_ff
    from glass.mob.esri.cf import cf_based_on_relations

    """
    Parameters
    """

    idir = '/mnt/disk1/jasp/rms/sub_by_conc'
    iid = 'BGRI11'
    grpid = 'idfreg'
    odir = '/mnt/disk1/jasp/rms/cfhospitais'

    facilities = '/mnt/disk1/jasp/rms/hospitais2017wJoin.shp'
    fcid = 'id_af'

    reltable = '/mnt/disk1/jasp/rms/areainf_hsp_2021.xlsx'
    relsheet = 'freg_hsp'
    groupfk = 'idfregr'
    fcfk    = 'id_hsparea'

    impedance = 'TravelTime'

    # Run procedure
    incidents = lst_ff(idir, file_format='.shp')

    results = lst_ff(odir, file_format='.shp', rfilename=True)

    for ishp in incidents:
        oshp = f"cf_{os.path.basename(ishp)}"
        
        if oshp in results:
            continue

        cf_based_on_relations(
            ishp, iid, grpid,
            facilities, fcid, reltable, relsheet,
            groupfk, fcfk,
            os.path.join(odir, oshp),
            impedance=impedance
        )

