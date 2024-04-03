"""
Network Analyst tools converted to Python
"""


import arcpy
import os


def polygons_to_facility(netdataset, polygons, facilities, outTbl,
                         oneway=None, rdv=None, junctions=None,
                         save_result_input=None):
    """
    Execute the Closest Facility tool after calculation of polygons
    centroids
    """
    
    from gesri.rd.shp       import shp_to_lyr
    from glass.cpu.arcg.mng.feat  import feat_to_pnt
    from gesri.tbl.cols   import add_col
    from glass.cpu.arcg.mng.fld   import calc_fld
    from glass.cpu.arcg.mng.joins import join_table    
    
    arcpy.env.overwriteOutput = True
    
    # Polygons to Points
    polLyr = shp_to_lyr(polygons)
    pntShp = os.path.join(
        os.path.dirname(polygons),
        os.path.splitext(os.path.basename(polygons))[0] + '_pnt.shp'
    )
    pntShp = feat_to_pnt(polLyr, pntShp, pnt_position='INSIDE')
    
    closest_facility(
        netdataset, facilities, pntShp, outTbl, 
        oneway_restriction=oneway, rdv=rdv, junc=junctions
    )
    
    field_output = 'dst' + os.path.splitext(os.path.basename(facilities))[0]
    add_col(outTbl, field_output[:10], "FLOAT", "10", "3")
    calc_fld(outTbl, field_output[:10], "[Total_Minu]")
    
    if save_result_input:
        add_col(outTbl, 'j', "SHORT", "6")
        calc_fld(outTbl, 'j', "[IncidentID]-1")
        join_table(polLyr, "FID", outTbl, "j", field_output[:10])


def folderPolygons_to_facility(inFolder, network, dest, outFolder,
                               oneway=None, rdv=None, junctions=None):
    """
    Run execute polygons_to_facility for every feature class in the inFolder
    """
    
    from glass.pys.oss import lst_ff
    
    lst_fc = lst_ff(inFolder, file_format='shp')
    
    for fc in lst_fc:
        out = os.path.join(
            outFolder,
            os.path.splitext(os.path.basename(fc))[0] + '.dbf'
        )
        
        polygons_to_facility(
            network, fc, dest, out,
            oneway=oneway, rdv=rdv, junctions=junctions
        )


def points_to_facility(netDataset, rdv_name, points, facilities, outTable,
                       oneway=None, save_result_input=None):
    """
    Execute Closest Facility and save the result in the points table
    """
    
    from gesri.tbl.cols   import add_col, calc_fld
    from glass.cpu.arcg.mng.joins import join_table
    
    arcpy.env.overwriteOutput = True
    
    closest_facility(
        netDataset, rdv_name, facilities, points, outTable,
        oneway_restriction=oneway
    )
    
    if save_result_input:
        add_col(outTable, 'j', "SHORT", 6)
        calc_fld(outTable, 'j', "[IncidentID]-1")
        join_table(points, "FID", outTable, "j", "Total_Minu")


def folderPoints_to_facility(netDataset, rdv_name, lst_points, facilities,
                             ONEWAY=None):
    """
    Execute points_to_facilities in loop
    """
    
    import os
    
    for fc in lst_points:
        points_to_facility(
            netDataset, rdv_name, fc, facilities,
            os.path.join(
                os.path.dirname(fc),
                'tbl_{}.dbf'.format(os.path.splitext(os.path.basename(fc))[0])
            ),
            oneway=ONEWAY, save_result_input=True
        )

