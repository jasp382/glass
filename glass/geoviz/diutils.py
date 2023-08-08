"""
Utilities to create data intervals
"""

def eval_intervals(int_, rnd_int, decplace, min_val):
    repeat = 1
    ndig = int(decplace)
    while repeat:
        # Check if we have need to repeat
        for _i_ in range(len(int_)):
            if not _i_:
                if rnd_int[_i_] == min_val:
                    repeat = 1
                    break
                
            else:
                if rnd_int[_i_] <= rnd_int[_i_ - 1]:
                    repeat = 1
                    break
                
                repeat = 0
            
        # Repeat intervals calculation if necessary
        if repeat:
            for __i in range(len(int_)):
                if not __i:
                    if rnd_int[__i] == min_val:
                        rnd_int[__i] = round(int_[__i], ndig + 1)
                
                else:
                    if rnd_int[__i] == rnd_int[__i - 1]:
                        rnd_int[__i] = round(int_[__i], ndig + 1)
                        
                    elif rnd_int[__i] < rnd_int[__i - 1]:
                        rnd_int[__i - 1] = round(int_[__i - 1], ndig + 1)
                
            ndig += 1
    
    return rnd_int, ndig
