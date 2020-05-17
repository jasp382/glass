"""
todo: confirma no documento no gdrive para ver se está de acordo e que informacao e q se devera manter
todo: ainda falta resolver pontos que aparecem nos dois dados vindos do IRD -
    fiz merge dos tres, sem geometric dissolve

                IRD vs CAE

INPUT::
    Industrial reporting dataset - IRD
        Pontos, representam industrias pelo IRD que contem 3 tipos de dados (installations, sites and prod. facilities)
        datasets (facilities, installtions, sites) were buffered, dissolved and merged into a single file, buffer of 25m

    Carta Areas Edificadas - CAE
        Areas contendo edificios

OUTPUT::

    Irv4vscae.shp @ results

        contem a uniao do IRDv4 e da CAE (valores na coluna TIPO NULL,1,2,3)

        NULL Porção do IRDv4 que cai fora do CAE aquando da união ou seja também faz parte do 2
        1 Apenas CAE presente (completamente)
        2 Apenas IRDv4 presente (completamente)
        3 IRDv4 e CAE presentes (completamente)

"""

import os
import subprocess
import re
import math
import pandas as pd
import numpy as np

from glass.rd.shp import shp_to_obj
from glass.wt.shp import df_to_shp

from glass.wenv.grs import run_grass
from glass.pys.oss import fprop
from glass.prop.prj import shp_epsg

# INPUT
#dados IRv4 - datasets (facilities, installtions, sites) were buffered, dissolved and merged into a single file, buffer of 25m
IRv4_shp='/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/dados/treino/IRDv4_ETRS89/fac_prod_sit.shp'
#dados dgt
cae_shp='/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/dados/ae/AreasEdificadas2018.shp'

# RESULTS
# IRv4/CAE intersection result
IRv4vscae='/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/results/Irv4vscae.shp'

#IRv4 com distancia aos dados cae
IRv4_dist_cae='/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/results/Irv4_dist_cae.shp'

# final results
IRv4_existe_cae ='/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/results/AE_IRD.shp'
IRv4_no_cae='/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/results/AE_IRdnCAE.shp'



# Start GRASS GIS Session

# Define Reference Raster -
refshp= '/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/dados/lim_adminis/PT/Lim_PT.shp'
workingfolder= '/media/mooi/tcr_1tb/pcloud/DGT_INESCC-hrl/codigo_alvaro/results/'

epsg = shp_epsg(refshp)

loc = 'pext'

# Start GRASS GIS Session
gb = run_grass(
    workingfolder, grassBIN='grass78', location=loc,
    srs=epsg
)
import grass.script.setup as gsetup

# __flag = 'o' if not lmtExt else 'or'

gsetup.init(gb, workingfolder, loc, 'PERMANENT')

# GRASS GIS Modules

from glass.it.shp import shp_to_grs, grs_to_shp
from glass.it.shp import overlay_grs, add_column_grs, distance_grs
from glass.gp.gen import dissolve


# Import data

IRv4_grs=shp_to_grs(IRv4_shp, fprop(IRv4_shp, 'fn'))
cae_grs=shp_to_grs(cae_shp, fprop(cae_shp, 'fn'))


# Union Irv4 CAE
IRv4cae=overlay_grs(IRv4_grs, cae_grs, 'or', 'union_Irv4cae')


#add coluna de atributos

dist={'dist_cae':'DOUBLE PRECISION'}
newIRv4_grs=add_column_grs(IRv4_grs, dist)


# distance Irv4 CAE
dist_IRv4cae=distance_grs(newIRv4_grs, cae_grs, 'dist', 'dist_cae')



# Export Data
IRv4distcae=grs_to_shp(dist_IRv4cae, IRv4_dist_cae, 'area')

IRv4_and_cae=grs_to_shp(IRv4cae, IRv4vscae, 'area')



gdf=shp_to_obj(IRv4_and_cae)

IRv4df=shp_to_obj(IRv4distcae)

gdf = gdf[~gdf.a_cat.isna()]

gdf['a_cat'] = gdf.a_cat.astype(int)
gdf['b_cat'] = gdf.b_cat.fillna(value=0)
gdf['b_cat'] = gdf.b_cat.astype(int)


# Count how many times we have the same a_cat

catcount = pd.DataFrame({
    'countcat' : gdf.groupby(['a_cat'])['a_cat'].agg('count')
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
    gdf.countcat > 1,
    2, gdf.fcat
)

fdf = pd.DataFrame({
    'existcae' : gdf.groupby(["a_cat"])['fcat'].agg('min')
}).reset_index()

IRv4df['cat'] = IRv4df.index + 1

#junçao dos dados do IRv4 com os dados do grau de existencia
IRv4df = IRv4df.merge(fdf, how='left', left_on='cat', right_on='a_cat')

IRv4df.rename(columns={
    'cat' : 'id_obj', 'cat_' : 'id_IRv4'
}, inplace=True)

IRv4df['fonte']    = 'IRv4'
IRv4df['classuos'] = '1211'
IRv4df['dist_cae'] = IRv4df.dist_cae.fillna(value=0)
IRv4df['existcae'] = IRv4df.existcae.fillna(value=-1)
IRv4df['existcae'] = IRv4df.existcae.astype(int)
IRv4df['areaha']   = IRv4df.geometry.area / 10000

IRv4df.drop(['a_cat'], axis=1, inplace=True)

#seleção de atributos do conjunto de dados do IRv4df
resultado_1=IRv4df[['id_obj','id_IRv4','geometry', 'fonte', 'classuos', 'existcae', 'areaha']]


#export to shapefille
df_to_shp(resultado_1, IRv4_existe_cae)

# seleção de das areas nao incluidas na CAE
no_cae=IRv4df[(IRv4df["existcae"]==0)]
no_cae=no_cae.reset_index()

no_cae['id_n_cae'] = no_cae.index + 1

resultado_2=no_cae[[
    'id_n_cae', 'id_obj','id_IRv4','geometry',
    'fonte', 'classuos', 'areaha', 'dist_cae'
]]

#export to shapefille
df_to_shp(resultado_2, IRv4_no_cae)
