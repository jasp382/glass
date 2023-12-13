"""
Raster Charts
"""


def rst_histogram(rst, bins, png, xaxis=None, figdim=(10,6)):
    """
    Create Raster Histogram
    """

    import matplotlib.pyplot as plt
    import seaborn as sns
    import rioxarray as rxr

    from glass.pys.oss import fprop

    sns.set(font_scale=1.5, style="whitegrid")

    # Open data 
    src = rxr.open_rasterio(rst, masked=True)

    fn = fprop(rst, 'fn')

    # Plot a histogram
    f, ax = plt.subplots(figsize=figdim)

    src.plot.hist(ax=ax, color="purple", bins=bins)

    if not xaxis:
        ax.set(
            title=f"Distribution of {fn} Raster",
            xlabel=fn, ylabel='Frequency'
        )
    else:
        ax.set(
            title=f"Distribution of {fn} Raster",
            xlabel=fn, ylabel='Frequency',
            xticks=xaxis
        )
    plt.savefig(png)

    return png

