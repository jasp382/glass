"""
Start GIS Sessions
"""


import os
import sys
from glass.pys     import execmd
from glass.pys.oss import del_folder

GRASS_BIN = 'grass78'

def start_grass_linux_newLocation(gisdb, location, srs=None,
                                  grassBin=None, overwrite=True):
    """
    Method to open GRASS GIS on Linux Systems
    Creates a new location
    
    Parameters:
    * gisdb - abs path to grass workspace
    * location - name for the grass location
    * srs - epsg or file to define spatial reference system of the location that 
    will be created
    """
    
    location_path = os.path.join(gisdb, location)
    
    # Delete location if exists
    if os.path.exists(location_path):
        if overwrite:
            del_folder(location_path)
        
        else:
            raise ValueError('GRASS GIS 7 Location already exists')
    
    grassbin = grassBin if grassBin else 'grass76'
    startcmd = grassbin + ' --config path'
    
    outcmd = execmd(startcmd)
    
    gisbase = outcmd.strip('\n')
    # Set GISBASE environment variable
    os.environ['GISBASE'] = gisbase
    # the following not needed with trunk
    os.environ['PATH'] += os.pathsep + os.path.join(gisbase, 'extrabin')
    # add path to GRASS addons
    home = os.path.expanduser("~")
    os.environ['PATH'] += os.pathsep + os.path.join(home, '.grass7', 'addons', 'scripts')    
    # define GRASS-Python environment
    gpydir = os.path.join(gisbase, "etc", "python")
    sys.path.append(gpydir)
    
    if type(srs) == int:
        srs = str(srs)
        startcmd = '{} -c epsg:{} -e {}'
    
    elif type(srs) == str:
        startcmd = '{} -c {} -e {}'
    
    else:
        srs = ""
        startcmd = '{}{} -e {}'
    
    outcmd = execmd(startcmd.format(
        grassbin, srs, location_path
    ))
    
    # Set GISDBASE environment variable
    os.environ['GISDBASE'] = gisdb
    
    # See if there is location
    if not os.path.exists(location_path):
        raise ValueError('NoError, but location is not created')
    
    return gisbase


def start_grass_linux_existLocation(gisdb, grassBin=None):
    """
    Method to start a GRASS GIS Session on Linux Systems
    Use a existing location
    """
    
    grassbin = grassBin if grassBin else GRASS_BIN
    startcmd = grassbin + ' --config path'
    
    outcmd = execmd(startcmd)
    
    gisbase = outcmd.strip('\n')
    # Set GISBASE environment variable
    os.environ['GISBASE'] = gisbase
    # the following not needed with trunk
    os.environ['PATH'] += os.pathsep + os.path.join(gisbase, 'extrabin')
    # add path to GRASS addons
    home = os.path.expanduser("~")
    os.environ['PATH'] += os.pathsep + os.path.join(home, '.grass7', 'addons', 'scripts')
    # define GRASS-Python environment
    gpydir = os.path.join(gisbase, "etc", "python")
    sys.path.append(gpydir)
    
    # Set GISDBASE environment variable
    os.environ['GISDBASE'] = gisdb
    
    return gisbase


def start_grass_win_newLocation(gisdb, location, srs=None, grassBin=None, overwrite=True):
    """
    Method to open GRASS GIS on MS Windows Systems
    Creates a new location
    
    Parameters:
    * gisdb - abs path to grass workspace
    * location - name for the grass location
    * srs - epsg or file to define spatial reference system of the location that 
    will be created
    
    
    To work, Path to GRASS GIS must be in the PATH Environment 
    Variable
    """
    
    # define database location
    location_path = os.path.join(gisdb, location)
    
    # Delete location if exists
    if os.path.exists(location_path):
        if overwrite:
            del_folder(location_path)
        
        else:
            raise ValueError(
                'GRASS GIS 7 Location already exists'
            )
    
    # the path to grass can't have white spaces
    grassbin = grassBin if grassBin else GRASS_BIN
    startcmd = grassbin + ' --config path'
    outcmd = execmd(startcmd)
    
    # Set GISBASE environment variable
    gisbase = outcmd.strip().split('\r\n')[0]
    os.environ['GRASS_SH'] = os.path.join(gisbase, 'msys', 'bin', 'sh.exe')
    os.environ['GISBASE'] = gisbase
    # define GRASS-Python environment
    gpydir = os.path.join(gisbase, "etc", "python")
    sys.path.append(gpydir)
    
    # Define Command
    if type(srs) == int:
        srs = str(srs)
        startcmd = '{} -c epsg:{} -e {}'
    
    elif type(srs) == str:
        startcmd = '{} -c {} -e {}'
    
    else:
        startcmd = '{}{} -e {}'
    
    # open grass
    outcmd = execmd(startcmd.format(
        grassbin, srs, location_path))
    
    # Set GISDBASE environment variable
    os.environ['GISDBASE'] = gisdb
    
    # See if there is location
    if not os.path.exists(location_path):
        raise ValueError('NoError, but location is not created')
    
    return gisbase


def start_grass_win_exisLocation(gisdb, grassBin=None):
    """
    Method to open GRASS GIS on MS Windows Systems
    Use an existing Location
    """
    
    grassbin = grassBin if grassBin else GRASS_BIN
    startcmd = grassBin + ' --config path'
    outcmd   = execmd(startcmd)
    
    # Set GISBASE environment variable
    gisbase = outcmd.strip().split('\r\n')[0]
    os.environ['GRASS_SH'] = os.path.join(gisbase, 'msys', 'bin', 'sh.exe')
    os.environ['GISBASE'] = gisbase
    # define GRASS-Python environment
    gpydir = os.path.join(gisbase, "etc", "python")
    sys.path.append(gpydir)
    
    # Set GISDBASE environment variable
    os.environ['GISDBASE'] = gisdb
    
    return gisbase


def run_grass(workspace, grassBIN=GRASS_BIN, location=None, srs=None):
    """
    Generic method that could be used to put GRASS GIS running in any Os
    
    To work on MSWindows, Path to GRASS Must be in the PATH Environment 
    Variables
    """
    
    from glass.pys.oss import os_name
    
    __os = os_name()
    
    if location:
        from glass.pys.oss import lst_fld
        
        # Check if location exists
        flds = lst_fld(workspace, name=True)
        
        if location in flds:
            base = start_grass_linux_existLocation(
                workspace, grassBin=grassBIN
            ) if __os == 'Linux' else start_grass_win_exisLocation(
                workspace, grassBin=grassBIN)
        
        else:
            base = start_grass_linux_newLocation(
                workspace, location, srs=srs, grassBin=grassBIN
            ) if __os == 'Linux' else start_grass_win_newLocation(
                workspace, location, srs=srs, grassBin=grassBIN
            ) if __os == 'Windows' else None
    
    else:
        base = start_grass_linux_existLocation(
            workspace, grassBin=grassBIN
        ) if __os == 'Linux' else start_grass_win_exisLocation(
            workspace, grassBin=grassBIN
        )
    
    if not base:
        raise ValueError((
            'Could not identify operating system'
        ))
    
    return base


"""
Manage regions
"""

def rst_to_region(__raster):
    from grass.pygrass.modules import Module
    
    r = Module(
        "g.region", raster=__raster, run_=False, quiet=True
    )
    
    r()


def shp_to_region(shp, cellsize=None):
    """
    Feature Class to region
    """

    from grass.pygrass.modules import Module

    r = Module("g.region", vector=shp, res=cellsize, run_=False, quiet=True)

    r()
