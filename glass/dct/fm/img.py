"""
Regular Image To Something
"""

def img_to_str(img):
    """
    Image data to Python String
    """

    from base64 import b64encode

    with open(img, 'rb') as imgb:
        base64_b = b64encode(imgb.read())

        base_s = base64_b.decode('utf-8')
    
    return base_s

