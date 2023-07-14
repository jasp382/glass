"""
Raster Charts
"""


def rst_histogram(rst, bins, png):
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
    f, ax = plt.subplots(figsize=(10, 6))

    src.plot.hist(ax=ax, color="purple", bins=bins)

    ax.set(
        title=f"Distribution of {fn} Raster",
        xlabel=fn, ylabel='Frequency'
    )
    plt.savefig(png)

    return png

