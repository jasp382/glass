"""
PYSTR related
"""

def random_str(char_number, all_char=None):
    """
    Generates a random string with numbers and characters
    """
    
    import random as r
    import string
    
    char = string.digits + string.ascii_letters
    if all_char:
        char += string.punctuation
    
    rnd = ''
    
    for i in range(char_number): rnd += r.choice(char)
    
    return rnd

