"""
Sampling tools
"""

import numpy as np


def split_binparray_randomly(rnum, nd, rshp, proportion, min_sample=None):
    """
    Extract some cells of one raster and save them into a new raster

    The cells not selected for extraction will be exported to other raster.
    """

    # Produce random samples for each value in inrst
    # Proportion of cells to select will be equal to proportion input

    # Get values
    val = np.unique(rnum)

    # Remove NoData
    if nd in val:
        val = val[val != nd]

    # Get absolute frequencies of all values in inrst
    rst_no_nd = rnum[rnum != nd]
    freq = np.bincount(rst_no_nd)
    freq = freq[freq != 0]

    if min_sample:
        val  = val[freq > min_sample]
        freq = freq[freq > min_sample]

    # Get number of cells to be selected for each value
    # Mantain indicated proportion
    ncells_byval = [int(round(v * proportion / 100.0, 0)) for v in freq]

    # Get index array
    idxref = np.arange(rnum.size)

    # Get array for each value
    # The values of new array will be the index
    vidx = [idxref[rnum == v] for v in val]

    # Get indicies of the cells to be extracted
    # Do it randomly
    rnd_num = [np.random.choice(
        vidx[i], size=ncells_byval[i],
        replace=False
    ) for i in range(len(ncells_byval))]

    # Create result
    res  = np.zeros(rnum.shape, dtype=rnum.dtype)
    nres = np.zeros(rnum.shape, dtype=rnum.dtype)

    # Place selected cells in the result array
    for v in range(val.shape[0]):
        np.place(res, np.isin(idxref, rnd_num[v]), val[v])
    
    # Get not selected cells
    np.copyto(nres, rnum, where=res == 0)

    # Place NoData
    np.place(res, rnum == nd, nd)
    np.place(res, res == 0, nd)
    np.place(nres, rnum == nd, nd)
    np.place(nres, nres == 0, nd)

    # Reshape
    res  = res.reshape(rshp)
    nres = nres.reshape(rshp)

    return res, nres

