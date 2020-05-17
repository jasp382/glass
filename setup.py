from setuptools import setup

setup(
    name='glass',
    version='0.0.1',
    description=(
        "The Geoscientific Library for Analysis of Spatial Systems (GLASS) is "
        "a free and open source library for geospatial data science. It consistes "
        "of a set of Python Methods to support the automatization of spatial data science "
        "activities based on Geographic Information Systems Software. "
        "These Python Methods could be included in any high-level spatial "
        "analysis application."
    ),
    url='https://github.com/jasp382/glass',
    author='jasp382',
    author_email='jpatriarca@mat.uc.pt',
    license='GPL',
    packages=[
        # ******************************************************************** #
        # ************************* Main module ****************************** #
        # ******************************************************************** #
        'glass'
        # ******************************************************************** #
        # *********************** Private modules **************************** #
        # ******************************************************************** #
        'glass.cons', 'glass.pys ',
        # ******************************************************************** #
        # ************************ Public modules **************************** #
        # ******************************************************************** #
        'glass.cls', 'glass.cls.txt',
        # ******************************************************************** #
        'glass.dct', 'glass.dct.geo', 'glass.dct.sql',
        # ******************************************************************** #
        'glass.dp', 'glass.dp.dsn', 'glass.dp.pd', 'glass.dp.xls',
        # ******************************************************************** #
        'glass.ete', 'glass.ete.osm2lulc',
        # ******************************************************************** #
        'glass.geo',
        'glass.geo.df', 'glass.geo.df.attr', 'glass.geo.df.gop',
        'glass.geo.df.nop', 'glass.geo.df.nop.sat',
        'glass.geo.df.prox', 'glass.geo.df.stats', 'glass.geo.df.tbl',
        'glass.geo.gql',
        'glass.geo.obj',
        'glass.geo.obj.gop', 'glass.geo.obj.lyr', 'glass.geo.obj.nop',
        'glass.geo.prop', 'glass.geo.prop.feat',
        'glass.geo.wenv',
        # ******************************************************************** #
        'glass.sql', 'glass.sql.q',
        # ******************************************************************** #
        'glass.webg', 'glass.webg.djg', 'glass.webg.gsrv', 'glass.webg.sld'
        # ******************************************************************** #
    ],
    include_package_data=True
)