"""
Python Objects Handling
"""

def pyv():
    """
    Return Python Version
    """

    import sys

    v = sys.version_info

    return f"{str(v.major)}.{str(v.minor)}"


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
    For 'glass.module', return the 'module' object
    """
    
    components = full_path.split('.')
    mod = __import__(components[0])
    
    for comp in components[1:]:
        mod = getattr(mod, comp)
    
    return mod



def reduce_memory_usage(df, verbose=True):
    import numpy as np
    
    numerics = ["int8", "int16", "int32", "int64", "float16", "float32", "float64"]
    start_mem = df.memory_usage().sum() / 1024 ** 2
    for col in df.columns:
        col_type = df[col].dtypes
        if col_type in numerics:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == "int":
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if (
                    c_min > np.finfo(np.float16).min
                    and c_max < np.finfo(np.float16).max
                ):
                    df[col] = df[col].astype(np.float16)
                elif (
                    c_min > np.finfo(np.float32).min
                    and c_max < np.finfo(np.float32).max
                ):
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
    end_mem = df.memory_usage().sum() / 1024 ** 2
    if verbose:
        print(
            "Mem. usage decreased to {:.2f} Mb ({:.1f}% reduction)".format(
                end_mem, 100 * (start_mem - end_mem) / start_mem
            )
        )
    return df

