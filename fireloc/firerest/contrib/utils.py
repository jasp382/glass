"""
Some utilities related with volunteers contributions
"""

def get_photo(byte_str, userid, resphoto=None, ctb=None):
    """
    Save byte array image in file
    """

    import os
    import datetime        as dt
    from glass.it.pht     import str_to_img
    from glass.pys.oss   import lst_ff
    from firerest.settings import GEOMEDIA_FOLDERS

    k = "CTB_PHOTOS" if not resphoto else "CTB_CLSPHOTOS"

    photofld = GEOMEDIA_FOLDERS.get(k, None)

    dtt = dt.datetime.utcnow().replace(microsecond=0)

    dstr = dtt.strftime("%Y%m%d_%H%M%S") if not ctb \
        else str(ctb)
    
    photos = lst_ff(photofld, rfilename=True)

    pic_name = f"pic_{str(userid)}_{dstr}.jpg"

    if pic_name in photos:
        pic_name = f"pic_{str(userid)}_{dstr}_1.jpg"

    str_to_img(byte_str, os.path.join(photofld, pic_name))
    
    return f'volu/photo/{pic_name}/'

