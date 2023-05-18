"""
Imagery corrections
"""


def lnd8_dn_to_ref(folder, img_format, meta_json, outWorkspace, srs):
    """
    Landsat8 digital numbers to surface reflectance
    """
    
    import math
    import json
    import os
    from glass.pys.oss    import lst_ff
    from glass.rd.rst   import rst_to_array
    from glass.prop.rst import get_cellsize, rst_stats
    from glass.wt.rst   import obj_to_rst
    
    
    def Get_RTA(Ml, Qcalc, Al):
        """
        Obtem Radiancia no Topo da Atmosfera
        
        Ml - relacao da radiancia multibanda
        Qcalc - imagem de satelite original
        Al - radiancia add band
        """
        
        Llambda = Ml * Qcalc + Al
        
        return Llambda
    
    def GetIrraSolar(d, Lmax, Pmax):
        """
        d - distancia da terra ao sol (com base no dia do ano em
        que a imagem foi recolhida)
        ESUN - irradiancia solar media exoatmosferica
        Lmax - radiancia maxima
        Pmax - reflectancia maxima
        """
        return (math.pi * d**2) * (Lmax/Pmax)
    
    def GetRefAparente(d, esun, rta, Z):
        """
        Reflectancia aparente
        Z - angulo zenital do sol
        """
        pp = math.pi * rta * d**2 / esun * math.cos(Z)
        return pp
    
    def GetRefSuperfice(DNmin, Ml, Al, IrrSolar, Z, d, RefAparente):
        """Reflectancia a superficie"""
        Lp = (Ml * DNmin + Al - 0.01 * IrrSolar) * (math.cos (Z) / math.pi * d**2)
        p = math.pi * (RefAparente - Lp) * d**2 / IrrSolar * math.cos(Z)
        return p
    
    lst_bands = lst_ff(folder, file_format=img_format)
    json_file = open(meta_json, 'r')
    json_data = json.load(json_file)
    cellsize = get_cellsize(lst_bands[0], gisApi='gdal')
    
    # Estimate Surface Reflectance for each band
    for bnd in lst_bands:
        # Convert images to numpy array
        img = rst_to_array(bnd)
        # Calculations of each pixel; store results on a new numpy array
        rta_array = Get_RTA(
            json_data[u"RADIANCE_MULT_BAND"][os.path.basename(bnd)],
            img,
            json_data[u"RADIANCE_ADD_BAND"][os.path.basename(bnd)]
        )
        solar_irradiation = GetIrraSolar(
            json_data[u"EARTH_SUN_DISTANCE"],
            json_data[u"RADIANCE_MAXIMUM_BAND"][os.path.basename(bnd)],
            json_data[u"REFLECTANCE_MAXIMUM_BAND"][os.path.basename(bnd)]   
        )
        ref_aparente_array = GetRefAparente(
            json_data[u"EARTH_SUN_DISTANCE"],
            solar_irradiation,
            rta_array,
            90 - json_data[u"SUN_ELEVATION"]
        )
        new_map = GetRefSuperfice(
            rst_stats(bnd, api='gdal')['MIN'],
            json_data[u"RADIANCE_MULT_BAND"][os.path.basename(bnd)],
            json_data[u"RADIANCE_ADD_BAND"][os.path.basename(bnd)],
            solar_irradiation,
            90 - json_data[u"SUN_ELEVATION"],
            json_data[u"EARTH_SUN_DISTANCE"],
            ref_aparente_array
        )
        obj_to_rst(
            new_map,
            os.path.join(outWorkspace, os.path.basename(bnd)),
            bnd
        )


"""
TODO: Adapt the following procedure to a python code


Processing for this file: 

1. r.in.gdal todas as imagens

2. i.landsat.toar 

3. i.topo.corr 
                     
4. exportar os dados em tif


Calling each raster layer to grass db - There must be a way of making the script work fast




------------------------------------- Loading all images
r.in.gdal --overwrite input=C:\Landsat\Land8Clip\bnd_01.TIF output=dnB.1
r.in.gdal --overwrite input=C:\Landsat\Land8Clip\bnd_02.TIF output=dnB.2
r.in.gdal --overwrite input=C:\Landsat\Land8Clip\bnd_03.TIF output=dnB.3
r.in.gdal --overwrite input=C:\Landsat\Land8Clip\bnd_04.TIF output=dnB.4
r.in.gdal --overwrite input=C:\Landsat\Land8Clip\bnd_05.TIF output=dnB.5
r.in.gdal --overwrite input=C:\Landsat\Land8Clip\bnd_06.TIF output=dnB.6
r.in.gdal --overwrite input=C:\Landsat\Land8Clip\bnd_07.TIF output=dnB.7
r.in.gdal --overwrite input=C:\Landsat\Land8Clip\bnd_08.TIF output=dnB.8
r.in.gdal --overwrite input=C:\Landsat\Land8Clip\bnd_09.TIF output=dnB.9
r.in.gdal --overwrite input=C:\Landsat\Land8Clip\bnd_10.TIF output=dnB.10
r.in.gdal --overwrite input=C:\Landsat\Land8Clip\bnd_11.TIF output=dnB.11

g.region rast=dnB.1@landsat8 


-------- conversao de DN para reflectancia e correccao atmosferica:---------------------


i.landsat.toar input_prefix=dnB. output_prefix=toar. metfile=C:\Landsat\Land8\LC82030322014167LGN00_MTL.txt sensor=ot8 method=dos4

----- importar o modelo de elevacao digital do terreno para o grass ------------------------------------

r.in.gdal input=C:\Landsat\mdt_WGS84.tif output=mdt_WGS --overwrite

--------------------------------------correccao topografica-----------------------------

90-(28.05822610) = 61.9417739
90 - (64.32430312) = 25.67569688
90 - 66.12573608 = 23.87426392

       1. Primeiro o modelo de illuminacao do terreno a partir da DEM

i.topo.corr -i --overwrite output=aster.illu basemap=mdt_WGS@landsat8
    zenith=23.87426392 azimuth=128.64173925

       2. A correcaoo topografica

i.topo.corr --overwrite input=toar.1,toar.2,toar.3,toar.4,toar.5,toar.6,toar.7,toar.8,toar.9,toar.10,toar.11 output=topo.
basemap=mdt_WGS@landsat8 zenith=23.87426392 azimuth=128.64173925 method=minnaert


---------------------------------------exportacao em tiff --------------------------------

g.rename --overwrite rast=topo..toar.1,topo..toar.01 
g.rename --overwrite rast=topo..toar.2,topo..toar.02 
g.rename --overwrite rast=topo..toar.3,topo..toar.03 
g.rename --overwrite rast=topo..toar.4,topo..toar.04 
g.rename --overwrite rast=topo..toar.5,topo..toar.05 
g.rename --overwrite rast=topo..toar.6,topo..toar.06 
g.rename --overwrite rast=topo..toar.7,topo..toar.07 
g.rename --overwrite rast=topo..toar.8,topo..toar.08 
g.rename --overwrite rast=topo..toar.9,topo..toar.09


Usar a ferramenta: i.group

i.group group=land8_estrela input=topo..toar.01@landsat8,topo..toar.02@landsat8,topo..toar.03@landsat8,topo..toar.04@landsat8,topo..toar.05@landsat8,topo..toar.06@landsat8,topo..toar.07@landsat8,topo..toar.08@landsat8,topo..toar.09@landsat8,topo..toar.10@landsat8,topo..toar.11@landsat8

# Nomes tem de estar em maiusculas
r.out.gdal --overwrite input=land8_estrela@landsat8 output=C:\Landsat\land8_estrela.tif format=GTiff
"""

"""FOR LANDSAT 7

Processing for this file: 

1. r.in.gdal todas as imagens

2. i.landsat.toar 

3. i.topo.corr 
                     
4. exportar os dados em tif


Calling each raster layer to grass db - There must be a way of making the script work fast




------------------------------------- Loading all images -------------------------------------------------------------------------------------------------
r.in.gdal --overwrite input=C:\Landsat\Land7Clip\Bnd_01.TIF output=dnB.1
r.in.gdal --overwrite input=C:\Landsat\Land7Clip\Bnd_02.TIF output=dnB.2
r.in.gdal --overwrite input=C:\Landsat\Land7Clip\Bnd_03.TIF output=dnB.3
r.in.gdal --overwrite input=C:\Landsat\Land7Clip\Bnd_04.TIF output=dnB.4
r.in.gdal --overwrite input=C:\Landsat\Land7Clip\Bnd_05.TIF output=dnB.5
r.in.gdal --overwrite input=C:\Landsat\Land7Clip\Bnd_06_1.TIF output=dnB.61
r.in.gdal --overwrite input=C:\Landsat\Land7Clip\Bnd_06_2.TIF output=dnB.62
r.in.gdal --overwrite input=C:\Landsat\Land7Clip\Bnd_07.TIF output=dnB.7
r.in.gdal --overwrite input=C:\Landsat\Land7Clip\Bnd_08.TIF output=dnB.8

g.region rast=dnB.1@Sao_pedro 


-------- conversao de DN para reflectancia e correccao atmosferica:---------------------


i.landsat.toar input_prefix=dnB. output_prefix=toar. metfile=C:\Landsat\LE72030322001171EDC00_MTL.txt sensor=tm7 method=dos3

----- importar o modelo de elevacao digital do terreno para o grass ------------------------------------

r.in.gdal input=C:\Landsat\mdt_WGS84.tif output=mdt_WGS --overwrite

--------------------------------------correccao topografica-----------------------------

90-(28.05822610) = 61.9417739
90 - (64.32430312) = 25.67569688
64.32430312 = elevacao do sol
       1. Primeiro o modelo de illuminacao do terreno a partir da DEM

i.topo.corr -i --overwrite output=aster.illu basemap=mdt_WGS@landsat7 zenith=25.67569688 azimuth=124.18532847

       2. A correcao topografica

i.topo.corr --overwrite input=toar.1,toar.2,toar.3,toar.4,toar.5,toar.61,toar.62,toar.7,toar.8 output=topo. basemap=mdt_WGS@landsat7 zenith=25.67569688 azimuth=124.18532847 method=minnaert


---------------------------------------exportacao em tiff --------------------------------

g.rename --overwrite rast=topo..toar.1,topo..toar.01 
g.rename --overwrite rast=topo..toar.2,topo..toar.02 
g.rename --overwrite rast=topo..toar.3,topo..toar.03 
g.rename --overwrite rast=topo..toar.4,topo..toar.04 
g.rename --overwrite rast=topo..toar.5,topo..toar.05 
g.rename --overwrite rast=topo..toar.61,topo..toar.061 
g.rename --overwrite rast=topo..toar.62,topo..toar.062
g.rename --overwrite rast=topo..toar.7,topo..toar.07 
g.rename --overwrite rast=topo..toar.8,topo..toar.08

Usar a ferramenta: i.group

i.group group=VERONICA input=topo..toar.01@landsat7,topo..toar.02@landsat7,topo..toar.03@landsat7,topo..toar.04@landsat7,topo..toar.05@landsat7,topo..toar.061@landsat7,topo..toar.062@landsat7,topo..toar.07@landsat7,topo..toar.08@landsat7


r.out.gdal --overwrite input=VERONICA@landsat7 output=C:\Landsat\VERONICA.TIF format=GTiff
"""
