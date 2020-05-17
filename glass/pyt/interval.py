"""
Methods to classified data
"""


"""
Calculate inverval breaks considering a datasample
"""

def _get_equal_int_(__max, __min, breakNumb):
    """
    Calculate interval breaks using Equal Invervals Method
    """
    
    int_break = (__max - __min) / float(breakNumb)

    breaks = []
    for i in range(breakNumb + 1):
        if i == 0:
            breaks.append(__min)
        elif i == breakNumb:
            breaks.append(__max)
        else:
            breaks.append(breaks[i-1] + int_break)

    return breaks

