"""
Change colors in layout files
"""

def change_color_on_map(in_img, rgbs, outimg):
    """
    Replace a certain color in one image for another color and write
    a new file

    rgbs = {
        (255, 255, 255) : (0, 0, 0),
        ...
    }
    """
    
    import numpy
    from PIL import Image
    
    img = Image.open(in_img)
    
    imgArray = numpy.array(img)

    for rgb in rgbs:
        r1, g1, b1 = rgb
    
        red, green, blue = imgArray[:, :, 0], imgArray[:, :, 1], imgArray[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
    
        imgArray[:, :, :3][mask] = list(rgbs[rgb])
    
    outImg = Image.fromarray(imgArray)
    
    outImg.save(outimg)
    
    return outimg

