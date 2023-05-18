"""
Image segmentation tools
"""

def img_segment(bands, threshold, radius, output, method=None, ascmd=True, seeds=None):
    """
    Run i.segment from GRASS GIS
    """

    method = method if method == 'region_growing'\
        or method == 'mean_shift' else 'region_growing'

    if not ascmd:
        from grass.pygrass.modules import Module

        m = Module(
            'i.segment', group=bands,
            output=output, method=method,
            threshold=threshold, radius=radius,
            minsize=5, seeds=seeds,
            overwrite=True, run_=False, quiet=True
        )

        m()
    
    else:
        from glass.pys import execmd

        _bands = ",".join(bands)
        seeds = '' if not seeds else f" seeds={seeds}"

        cmd = execmd((
            f"i.segment group={_bands} "
            f"output={output} method={method} "
            f"threshold={str(threshold)} radius={str(radius)} "
            f"minsize=5{seeds} --overwrite --quiet"
        ))
    
    return output
