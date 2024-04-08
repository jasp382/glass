"""
Data to cube
"""

def check_compatibility(datasets, crs_list,):
    """Verifica se todos os datasets têm mesmo shape e CRS."""
    shapes   = [ds.rio.shape for ds in datasets]
    if len(set(shapes)) > 1:
        raise ValueError(f"Shapes diferentes entre os GeoTIFFs: {shapes}")
    if len(set(crs_list)) > 1:
        raise ValueError(f"Sistemas de coordenadas diferentes: {crs_list}")


def gtifs_to_cube(geotifs, ocube, chunksize=(512, 512), featname=None):
    """
    GeoTiff's to Data Cube
    """

    import os
    import xarray as xr
    import numcodecs

    from glass.pys.oss import lst_ff, fprop
    from glass.rd.rst import rst_to_dset
    from glass.prop.prj import get_epsg

    if isinstance(geotifs, str) == str and os.path.isdir(geotifs):
        geotifs = lst_ff(geotifs, file_format='.tif')

    # Carregar GeoTIFFs com chunks para tirar proveito da RAM disponível
    datasets = rst_to_dset(geotifs, chunks=chunksize, api='rio')

    check_compatibility(datasets, [get_epsg(r) for r in geotifs])

    # Empilhar as features na dimensão 'feature'
    data_cube = xr.concat(datasets, dim='feature')

    # Nomear a dimensão 'feature' conforme os ficheiros
    featname = None if type(featname) != list and len(featname) != len(geotifs) \
        else featname
    
    if not featname: 
        fnames = [fprop(rst, 'fn') for rst in geotifs]
    
    else:
        fnames = featname
    
    data_cube = data_cube.assign_coords(feature=fnames)

    # Save to file
    if not data_cube.name:
        data_cube.name = 'cubefeats'

    compressor = numcodecs.Zlib(level=5)
    data_cube.to_zarr(ocube, encoding={
        data_cube.name: {'compressor': compressor, 'chunks': (1, chunksize[0], chunksize[1])}   
    })

    return ocube

