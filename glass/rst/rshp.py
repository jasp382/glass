"""
Reshape Raster Tools
"""


def rshp_to_data(in_arr, ndval, left, cellx, top, celly):
    """
    Pick Raster array and delete all rows and cols with only
    NoData Values

    Returns new array and new top and left
    """

    import numpy as np

    X = in_arr.reshape((in_arr.shape[0] * in_arr.shape[1]))
    I = np.arange(X.shape[0])

    np.place(I, X == ndval, -1)
    I = I[I != -1]

    # Get Minimum and Maximum Row Indexes
    # considering the rows with cells with data
    i_row = I / in_arr.shape[0]
    i_row = i_row.astype(np.uint32)
    min_row, max_row = i_row.min(), i_row.max()

    # Get Minimum and Maximum Column Indexes
    i_col = I - (i_row * in_arr.shape[1])
    min_col, max_col = i_col.min(), i_col.max()

    # Get Clipped array
    clipnum = in_arr[min_row:max_row+1, min_col:max_col+1]

    # Get new left and new top
    new_left = left + (cellx * min_col)
    new_top  = top  + (celly * min_row)

    return clipnum, new_left, new_top

