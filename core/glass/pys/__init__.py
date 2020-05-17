"""
Python Objects Handling
"""

def pyv():
    """
    Return Python Version
    """

    import sys

    v = sys.version_info

    return "{}.{}".format(str(v.major), str(v.minor))


def obj_to_lst(obj):
    """
    A method uses a list but the user gives other type of object
    
    This method will see if the object is not a list and convert it to a list
    """

    return obj if type(obj) == list else [obj] if obj != None else None


def execmd(cmd):
    """
    Execute a command and provide information about the results
    """
    import subprocess
    
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    out, err = p.communicate()
    
    if p.returncode != 0:
        raise ValueError((
            'Message: Command execution ended with error\n'
            f'Command was: {cmd}\n'
            f'Output: {out.decode("utf-8")}\n'
            f'Error: {err.decode("utf-8")}'
        ))
    
    else:
        return out.decode('utf-8')


def __import(full_path):
    """
    For 'glass.g.module', return the 'module' object
    """
    
    components = full_path.split('.')
    mod = __import__(components[0])
    
    for comp in components[1:]:
        mod = getattr(mod, comp)
    
    return mod
