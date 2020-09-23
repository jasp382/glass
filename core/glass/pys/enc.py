"""
Encoding Stuff
"""

def str_to_ascii(__str):
    """
    String to numeric code
    """
    
    return ''.join(str(ord(c)) for c in __str)


def id_encodefile(file__):
    """
    Find encoding of file using chardet
    """
    
    from chardet.universaldetector import UniversalDetector
    
    detector = UniversalDetector()
    
    for l in open(file__):
        detector.feed(l)
        
        if detector.done:
            break
    
    detector.close()
    
    return detector.result['encoding']

