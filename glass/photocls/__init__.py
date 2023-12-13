"""
Fire detection on images with YOLOv4 custom model to consider two classes: Fire and Smoke

"""

def img_firedetectv1(imgLoc):
    """

    inputs::
    imgLoc - path to image to be used in fire and smoke detection
    darknetloc - path to folder containg the built darknet repo
        assumes the presence of weights final in darknet folder - yolov4_treino_maisteste_final.weights
        assumes the presence of cfg network config file  in darknet folder - yolov4_treino_416.cfg
        assumes that data/coco.names contains only two lines, 1st with Fire 2nd with Smoke

        see requirements to build darknet in DARKNET_INSTALL.md

    outputs::
    string with detection result yes/no

    Example:

    imgloc = 'data/dog.jpg'
    darknetloc = '/path/to/darknet/folder/darknet/'
    res = img_firedetect(imgloc,darknetloc)
    print(res)
    """

    import subprocess
    from glass.firecons.photocls import darkpath

    dpath = darkpath()

    #command
    bashCommand = (
        './darknet detect yolov4_treino_416.cfg '
        'yolov4_treino_maisteste_final.weights '
        f'{imgLoc} -thresh 0.3 -dont_show'
    )

    proc = subprocess.Popen(
        bashCommand.split(),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=dpath
    )

    output, error = proc.communicate()

    # digest results for final information, 
    # if Smoke or Fire in output string then it was detected:
    if str(output).find('Smoke') == -1 and str(output).find('Fire') == -1:
        res= 'No fire or smoke in the image'

    else:

        res = 'Smoke or Fire detected in the image.'


    return output, res


def img_firedetect(imgLoc, outimg=None):
    """

    inputs::
    imgLoc - path to image to be used in fire and smoke detection
    darknetloc - path to folder containg the built darknet repo
        assumes the presence of weights final in darknet folder - yolov4_treino_maisteste_final.weights
        assumes the presence of cfg network config file  in darknet folder - yolov4_treino_416.cfg
        assumes that data/coco.names contains only two lines, 1st with Fire 2nd with Smoke

        see requirements to build darknet in DARKNET_INSTALL.md

    outputs::
    string with detection result yes/no

    Example:

    imgloc = 'data/dog.jpg'
    darknetloc = '/path/to/darknet/folder/darknet/'
    res = img_firedetect(imgloc,darknetloc)
    print(res)
    """

    import subprocess
    import os
    from glass.firecons.photocls import darkpath
    from glass.pys.oss   import copy_file

    dpath = darkpath()

    #command
    bashCommand = (
        './darknet detect yolov4_treino_416.cfg '
        'yolov4_treino_maisteste_final.weights '
        f'{imgLoc} -thresh 0.3 -dont_show'
    )

    proc = subprocess.Popen(
        bashCommand.split(),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=dpath
    )

    output, error = proc.communicate()

    # digest results for final information, 
    outstr = output.decode()

    outlst = outstr.split(' \n ')
    results = outlst[-1].split('\n')[2:-1]

    outp = {"fire": [], "smoke" : []}

    for r in results:
        if r.startswith('Fire'):
            outp["fire"].append(int(r.replace('Fire: ', '').replace('%', '')))
    
        elif r.startswith('Smoke'):
            outp["smoke"].append(int(r.replace('Smoke: ', '').replace('%', '')))
    
    # Copy prediciton image if outimg
    if outimg:
        copy_file(os.path.join(dpath, 'predictions.jpg'), outimg)

    return outp

