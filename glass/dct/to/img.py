"""
Something to regular image
"""

def str_to_img(s, img):
    """
    Byte String image to real image
    """

    from base64 import b64decode

    img_data = b64decode(s)

    with open(img, 'wb') as i:
        i.write(img_data)
    
    return img
