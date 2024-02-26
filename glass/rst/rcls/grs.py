"""
GRASS GIS Raster Reclassify Methods
"""

import os


def grs_rcls(inrst, rcls_rules, orst, as_cmd=None):
    """
    GRASS GIS Reclassify
    """

    if not as_cmd:
        from grass.pygrass.modules import Module
        
        r = Module(
            'r.reclass', input=inrst, output=orst, rules=rcls_rules,
            overwrite=True, run_=False, quiet=True
        )
        
        r()
    
    else:
        from glass.pys import execmd

        rcmd = execmd((
            f"r.reclass input={inrst} output={orst} "
            f"rules={rcls_rules} --overwrite --quiet"
        ))

    return orst


def rcls_rules(dic, out_rules):
    """
    Write reclassify rules file
    """

    if os.path.splitext(out_rules)[1] != '.txt':
        out_rules = os.path.splitext(out_rules)[0] + '.txt'
    
    with open(out_rules, 'w') as txt:
        for k in dic:
            if type(k) == tuple:
                thru = [
                    f'{str(k[i-1])} thru {str(k[i])}'
                    for i in range(1, len(k), 2)
                ]

                txt.write(f'{"  ".join(thru)}  = {str(dic[k])}\n')
            
            else:
                txt.write(f'{str(k)}  = {str(dic[k])}\n')

    return out_rules


def interval_rules(dic, out_rules):
    """
    Write rules file for reclassify - in this method, intervals will be 
    converted in new values
    
    dic = {
        [lower_class_value, upper_class_value] : new_value1,
        (lower_class_value, upper_class_value) : new_value2,
        ...,
        (lower_class_value, upper_class_value) : new_valuen
    }
    """
    
    if os.path.splitext(out_rules)[1] != '.txt':
        out_rules = os.path.splitext(out_rules)[0] + '.txt'
    
    with open(out_rules, 'w') as txt:
        for nv in dic:
            thru = [
                f'{str(nv[i-1])} thru {str(nv[i])}'
            for i in range(1, len(nv), 2)]

            txt.write(f'{"  ".join(thru)}  = {str(dic[nv])}\n')
        
        txt.close()
    
    return out_rules


def category_rules(dic, out_rules):
    """
    Write rules file for reclassify - in this method, categorical values will be
    converted into new designations/values
    
    dic = {
        old_value : new_value,
        old_value : new_value,
        ...
    }
    """
    
    if os.path.splitext(out_rules)[1] != '.txt':
        out_rules = os.path.splitext(out_rules)[0] + '.txt'
    
    with open(out_rules, 'w') as txt:
        for k in dic:
            txt.write(
                '{n}  = {o}\n'.format(o=str(dic[k]), n=str(k))
            )
        
        txt.close()
    
    return out_rules


def onlydata_rules(orules, mindata=1, maxdata=66000):
    """
    Write rules to reclassify GRASS GIS Raster

    Data = 0; NoData = null
    """

    with open(orules, 'w') as txt:
        txt.write(f'{str(mindata)} thru {str(maxdata)} = 1\n')
        txt.write('*    = NULL\n')
        txt.write('end')
    
    return orules


def set_null(rst, value, ascmd=None):
    """
    Null in Raster to Some value
    """
    
    if not ascmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            'r.null', map=rst, setnull=value, run_=False, quiet=True
        )
        
        m()
    
    else:
        from glass.pys import execmd
        
        rcmd = execmd(f"r.null map={rst} setnull={value} --quiet")


def null_to_value(rst, value, as_cmd=None):
    """
    Give a numeric value to the NULL cells
    """
    
    if not as_cmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            'r.null', map=rst, null=value, run_=False, quiet=True
        )
        m()
    
    else:
        from glass.pys import execmd
        
        rcmd = execmd(f"r.null map={rst} null={value} --quiet")

