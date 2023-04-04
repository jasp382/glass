
osm_ref_tags = {
    "TABLE": '/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/dados/dados_OSM/osm_features_2021_v2.xlsx',
    "SHEET": 'osm_features',
    "LULC_COL": 'L4',
    "KEY_COL": "key",
    "VALUE_COL": "value",
    "GEOM_COL": "geom"
}

osmdata = {
    "FILE": '/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/dados/dados_OSM/osm_CBR.xml',
    "DB": 'dgt_osmcbr',
    "TABLE": "multipolygons",
    "DBSET": "local"
}

ref_edificado = [
    '1141', '1151', '1211', '1221',
    '1222', '1223', '1231', '1241',
    '1251', '1252', '1254', '1255',
    '1256', '1257', '1253', '1612',
    '1631', '1632', '1633', '1651',
    '16', '143', '1431', '1432'
]

lulccls = 'lulc_cls'

caeshp = '/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/dados/treino/AreasEdificadas2018_CBR.shp'

refshp = '/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/dados/lim_adminis/PT/Lim_PT.shp'

epsg = 3763

# OSM LULC result
lulcshp = '/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/dados/dados_OSM/teste/AE_OSM.shp'
osm_no_cae = '/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/dados/dados_OSM/teste/AE_OSMnCAE.shp'

# OSM/CAE intersection result
osmvscae = '/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/dados/dados_OSM/teste/osmvscae.shp'

import os
import pandas as pd
import numpy as np

from dgt.it.osm import osm_to_psql
from dgt.it.shp import dbtbl_to_shp
from dgt.wenv.grs import run_grass
from dgt.dp.torst import shp_to_rst
from dgt.rd.shp import shp_to_obj
from dgt.wt.shp import df_to_shp

from dgt.prop.sql import cols_name
from dgt.rd import tbl_to_obj
from dgt.sql.q import exec_write_q
from dgt.sql.db import create_db
from dgt.pys.oss import mkdir, fprop


# Prepare workspace
ws = mkdir(os.path.join(
    os.path.dirname(lulcshp), 'grswork'
), overwrite=True)

create_db(osmdata["DB"], api='psql', overwrite=True)

osm_to_psql(osmdata["FILE"], osmdata["DB"])
'dgt_osmcbr'

osm_tags = tbl_to_obj(osm_ref_tags["TABLE"], sheet=osm_ref_tags["SHEET"])

osm_tags = osm_tags[osm_tags[osm_ref_tags["GEOM_COL"]] == 'Polygon']

osm_tags['sevtags'] = osm_tags[osm_ref_tags["LULC_COL"]].str.contains(';')

osm_tags = osm_tags[osm_tags.sevtags != True]

# Create key/value column
osm_tags.loc[:, osm_ref_tags["VALUE_COL"]] = osmdata["TABLE"] + "." + \
                                             osm_tags[osm_ref_tags["KEY_COL"]] + \
                                             "='" + osm_tags[osm_ref_tags["VALUE_COL"]] + "'"

# Add new column to multipolygons table
# Update it adding an LULC class

cols = cols_name(osmdata["DB"], osmdata['TABLE'], dbset=osmdata["DBSET"])

qs = [] if "lulc_cls" in cols else [(
    f"ALTER TABLE {osmdata['TABLE']} ADD COLUMN "
    "lulc_cls integer"
)]

for cls in osm_tags[osm_ref_tags["LULC_COL"]].unique():
    # Se uma feature estiver associada a duas TAGS que dizem respeito a classes
    # diferentes, a classe da feature será a última classe considerada
    # Abordagem multitag vai resolver este problema.
    __osmtags = osm_tags[osm_tags[osm_ref_tags["LULC_COL"]] == cls]

    qs.append((
        f"UPDATE {osmdata['TABLE']} SET lulc_cls={str(cls)} "
        f"WHERE {str(__osmtags[osm_ref_tags['VALUE_COL']].str.cat(sep=' OR '))}"
    ))

# RUN queries
exec_write_q(osmdata["DB"], qs, api='psql', dbset=osmdata["DBSET"])

# Export shapefile with data
whr = " OR ".join([f"lulc_cls={c}" for c in ref_edificado])

q = (
    f'SELECT ogc_fid, osm_id, name, lulc_cls, '
    'building, amenity, landuse, '
    f'ST_Transform(wkb_geometry, {str(epsg)}) AS geom '
    f'FROM {osmdata["TABLE"]} '
    f'WHERE {whr}'
)

osmlulc = dbtbl_to_shp(
    osmdata["DB"], q, 'geom', os.path.join(ws, 'osmlulc.shp'),
    tableIsQuery=True, api='pgsql2shp', epsg=epsg,
    dbset=osmdata["DBSET"]
)



#Dissolvealllulcclassespolygons and intersect OSM with CAE

# Start GRASS GIS Session

bname = fprop(refshp, 'fn')

refrst = shp_to_rst(
    refshp, None, 10, 0, os.path.join(
        ws, f'rst{bname}.tif'
    )
)

loc = 'locwork'
gb = run_grass(ws, location=loc, srs=refrst)

import grass.script.setup as gsetup

gsetup.init(gb, ws, loc, 'PERMANENT')

# GRASS GIS Modules
from dgt.it.shp import shp_to_grs, grs_to_shp
from dgt.defs_alvaro.col import add_fields  # , cols_calc
from dgt.it.shp import add_table
from dgt.it.shp import dissolve
from dgt.gp.ovl import grsunion
from dgt.it.shp import overlay_grs, add_column_grs, distance_grs


# Import data
osmlulcgrs = shp_to_grs(osmlulc, fprop(osmlulc, 'fn'))
caegrs = shp_to_grs(caeshp, fprop(caeshp, 'fn'))

# Dissolve
lulcdiss = dissolve(osmlulcgrs, 'lulc_cls', 'osmlulcdiss', api='pygrass')

add_table(lulcdiss, None, 'lulc_cls', asCMD=False)

disscat = grs_to_shp(lulcdiss, os.path.join(
    ws, 'osmlulcdiss.shp'
), 'area')

lulcdiss = shp_to_grs(disscat, fprop(disscat, 'fn'))


# Union OSM CAE
osmcae = grsunion(lulcdiss, caegrs, 'lulcunion')

# add coluna de atributos

dist = {'dist_cae': 'DOUBLE PRECISION'}
newlulcdiss = add_column_grs(lulcdiss, dist)

# distance Irv4 CAE
dist_osmcae = distance_grs(newlulcdiss, caegrs, 'dist', 'dist_cae')

# Export
osmdistcae = grs_to_shp(dist_osmcae, os.path.join(ws, 'osm_dist_cae.shp'), 'area')

osm_and_cae = grs_to_shp(osmcae, osmvscae, 'area')


gdf = shp_to_obj(osm_and_cae)

osmdf = shp_to_obj(osmdistcae)
gdf = gdf[~gdf.a_cat.isna()]

gdf['a_cat'] = gdf.a_cat.astype(int)
gdf['b_cat'] = gdf.b_cat.fillna(value=0)
gdf['b_cat'] = gdf.b_cat.astype(int)
# Count how many times we have the same a_cat

catcount = pd.DataFrame({
    'countcat': gdf.groupby(['a_cat'])['a_cat'].agg('count')
}).reset_index()

catcount.rename(columns={'a_cat': 'acaty'}, inplace=True)
# Join
gdf = gdf.merge(catcount, how='inner', left_on='a_cat', right_on='acaty')
# Get classes
gdf['fcat'] = -1

gdf['fcat'] = np.where(
    (gdf.countcat == 1) & (gdf.b_cat == 0),
    0, gdf.fcat
)

gdf['fcat'] = np.where(
    (gdf.countcat == 1) & (gdf.b_cat > 0),
    1, gdf.fcat
)

gdf['fcat'] = np.where(
    gdf.countcat > 1, 2, gdf.fcat
)
fdf = pd.DataFrame({
    'existcae': gdf.groupby(["a_cat"])['fcat'].agg('min')
}).reset_index()
osmdf['cat'] = osmdf.index + 1

osmdf = osmdf.merge(fdf, how='left', left_on='cat', right_on='a_cat')
print(osmdf)
osmdf.rename(columns={
    'cat': 'id_obj', 'lulc_cls': 'classuos'
}, inplace=True)

osmdf['fonte'] = 'osm'
osmdf['classuos'] = osmdf.classuos.astype(str)
osmdf['dist_cae'] = osmdf.dist_cae.fillna(value=0)
osmdf['existcae'] = osmdf.existcae.fillna(value=-1)
osmdf['existcae'] = osmdf.existcae.astype(int)
osmdf['areaha'] = osmdf.geometry.area / 10000

osmdf.drop(['a_cat'], axis=1, inplace=True)
print(osmdf)
# seleção de atributos do conjunto de dados do osmdf
resultado_1 = osmdf[['id_obj', 'geometry', 'fonte', 'classuos', 'existcae', 'areaha']]
df_to_shp(resultado_1, lulcshp)
no_cae = osmdf[(osmdf["existcae"] == 0)]
no_cae = no_cae.reset_index()

no_cae['id_n_cae'] = no_cae.index + 1
resultado_2 = no_cae[['id_n_cae', 'id_obj', 'geometry', 'fonte', 'classuos', 'areaha', 'dist_cae']]
df_to_shp(resultado_2, osm_no_cae)