"""
Chunksizes estimation
"""

def find_chunksize(roidf, nbands, bytes_per_px, nscenes,
                   res=10, ram_gb=16, target_mb=150):
    """
    Returns (time, band, y, x) visando ~alvo_mb por chunk
    - roi_gdf: GeoDataFrame do AOI (EPSG:4326)
    - n_bandas: ex. 3 (B02,B03,B04)
    - bytes_por_px: 2 para uint16, 4 para float32
    - n_cenas_mes: nº de itens do mês (pode medir após a busca STAC)
    - res: resolução em metros (10 para S2 10 m)
    - epsg_out: grelha de saída (use 3857 se está a usar epsg=3857 no stackstac)
    - ram_gb: RAM por worker
    - alvo_mb: alvo de memória por chunk (50–250 MB típico)
    """

    from glass.prop.prj import df_epsg

    epsg = df_epsg(roidf)

    # 1) pixels of roi
    bounds_m = roidf.total_bounds
    with_m   = max(1.0, bounds_m[2] - bounds_m[0])
    height_m = max(1.0, bounds_m[3] - bounds_m[1])

    px_x_total = max(1, int(with_m / res))
    px_y_total = max(1, int(height_m / res))

    # 2) choose base for y/x (multiplos 256)