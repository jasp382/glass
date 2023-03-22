"""
Methods to interact with the Operating System
"""

import os
import re

def os_name():
    import platform
    return str(platform.system())


def cpu_cores(api='os'):
    """
    Return CPU Cores Number 
    """

    if api == 'os':
        return os.cpu_count()
    else:
        import multiprocessing
        return multiprocessing.cpu_count()


def fprop(__file, prop, forceLower=None, fs_unit=None):
    """
    Return some property of file

    prop options:
    * filename or fn - return filename
    """

    from glass.pys import obj_to_lst

    prop = obj_to_lst(prop)

    result = {}

    fn, ff = os.path.splitext(os.path.basename(__file))

    if 'filename' in prop or 'fn' in prop:
        result['filename'] = fn if not forceLower else fn.lower()
    
    if 'fileformat' in prop or 'ff' in prop:
        result['fileformat'] = ff
    
    if 'filesize' in prop or 'fs' in prop:
        fs_unit = 'MB' if not fs_unit else fs_unit

        fs = os.path.getsize(__file)

        if fs_unit == 'MB':
            fs  = (fs / 1024.0) / 1024
        
        elif fs_unit == 'KB':
            fs = fs / 1024.0
        
        result['filesize'] = fs
    
    if len(prop) == 1:
        if prop[0] == 'fn':
            return result['filename']
        elif prop[0] == 'ff':
            return result['fileformat']
        elif prop[0] == 'fs':
            return result['filesize']
        else:
            return result[prop[0]]
    else:
        return result


def lst_ff(w, file_format=None, filename=None, rfilename=None):
    """
    List the abs path of all files with a specific extension on a folder
    """
    
    from glass.pys import obj_to_lst
    
    # Prepare file format list
    if file_format:
        formats = obj_to_lst(file_format)
        
        for f in range(len(formats)):
            if formats[f][0] != '.':
                formats[f] = '.' + formats[f]
    
    # List files
    r = []
    for (d, _d_, f) in os.walk(w):
        r.extend(f)
        break
    
    # Filter files by format or not
    if not file_format:
        if not rfilename:
            t = [os.path.join(w, i) for i in r]
        else:
            t = [i for i in r]
    
    else:
        if not rfilename:
            t = [
                os.path.join(w, i) for i in r
                if os.path.splitext(i)[1] in formats
            ]
        else:
            t = [i for i in r if os.path.splitext(i)[1] in formats]
    
    # Filter by filename
    if not filename:
        return t
    
    else:
        filename = obj_to_lst(filename)
        
        _t = []
        for i in t:
            fn = fprop(i, 'fn') if not rfilename else i
            if fn in filename:
                _t.append(i)
        
        return _t


def lst_fld(w, name=None):
    """
    List folders path or name in one folder
    """
    
    foldersname = []
    for (dirname, dirsname, filename) in os.walk(w):
        foldersname.extend(dirsname)
        break
    
    if name:
        return foldersname
    
    else:
        return [os.path.join(w, fld) for fld in foldersname]


def list_folders_files(w, name=None):
    """
    List folders and files path or name
    """
    
    fld_file = []
    for (dirname, dirsname, filename) in os.walk(w):
        fld_file.extend(dirsname)
        fld_file.extend(filename)
        break
    
    if name:
        return fld_file
    
    else:
        return [os.path.join(w, f) for f in fld_file]


def list_folders_subfiles(path, files_format=None,
                          only_filename=None):
    """
    List folders in path and the files inside each folder
    """
    
    folders_in_path = lst_fld(path)
    
    out = {}
    for folder in folders_in_path:
        out[folder] = lst_ff(
            folder, file_format=files_format
        )
        
        if only_filename:
            for i in range(len(out[folder])):
                out[folder][i] = os.path.basename(out[folder][i])
    
    return out

"""
Manage folders
"""

def mkdir(folder, randName=None, overwrite=True):
    """
    Create a new folder
    Replace the given folder if that one exists
    """
    
    if randName:
        import random
        chars = '0123456789qwertyuiopasdfghjklzxcvbnm'
        
        name = ''
        for i in range(10):
            name+=random.choice(chars)
        
        folder = os.path.join(folder, name)
    
    if os.path.exists(folder):
        if overwrite:
            import shutil
            
            shutil.rmtree(folder)
        else:
            raise ValueError(f"{folder} already exists")
    
    os.mkdir(folder)
    
    return folder


def fld_exists(fld):
    """
    Check if one folder exists!
    """

    flds = lst_fld(os.path.dirname(fld), name=True)

    if os.path.basename(fld) in flds:
        return 1
    else:
        return None


"""
Delete things
"""

def del_folder(folder):
    """
    Delete folder if exists
    """
    
    import shutil
    
    if os.path.exists(folder) and os.path.isdir(folder):
        shutil.rmtree(folder)


def del_file(_file):
    """
    Delete files if exists
    """
    
    from glass.pys import obj_to_lst
    
    for ff in obj_to_lst(_file):
        if os.path.isfile(ff) and os.path.exists(ff):
            os.remove(ff)



def del_file_folder_tree(fld, file_format):
    """
    Delete all files with a certain format in a folder and sub-folders
    """
    
    if file_format[0] != '.':
        file_format = '.' + file_format
    
    for (dirname, sub_dir, filename) in os.walk(fld):
        for f in filename:
            if os.path.splitext(f)[1] == file_format:
                os.remove(os.path.join(dirname, f))


def del_files_by_name(folder, names):
    """
    Del files with some name
    """
    
    
    lst_files = lst_ff(folder, filename=names)
    
    for f in lst_files:
        del_file(f)


def del_files_by_partname(folder, partname):
    """
    If one file in 'folder' has 'partname' in his name, it will be
    deleted
    """
    
    files = lst_ff(folder)
    
    for _file in files:
        if partname in os.path.basename(_file):
            del_file(_file)


"""
Rename things
"""

def rename_files_with_same_name(folder, oldName, newName):
    """
    Rename files in one folder with the same name
    """
    
    _Files = lst_ff(folder, filename=oldName)
    
    Renamed = []
    for f in _Files:
        newFile = os.path.join(folder, newName + fprop(f, 'ff'))
        os.rename(f, newFile)
        
        Renamed.append(newFile)
    
    return Renamed


def onFolder_rename(fld, toBeReplaced, replacement, only_files=True,
                    only_folders=None):
    """
    List all files in a folder; see if the filename includes what is defined
    in the object 'toBeReplaced' and replace this part with what is in the
    object 'replacement'
    """
    

    if not only_files and not only_folders:
        files = list_folders_files(fld)

    elif not only_files and only_folders:
        files = lst_fld(fld)

    elif only_files and not only_folders:
        files = lst_ff(fld)

    for __file in files:
        if os.path.isfile(__file):
            filename = os.path.splitext(os.path.basename(__file))[0]
        else:
            filename = os.path.basename(__file)

        if toBeReplaced in filename:
            renamed = filename.replace(toBeReplaced, replacement)

            if os.path.isfile(__file):
                renamed = renamed + os.path.splitext(os.path.basename(__file))[1]

            os.rename(
                __file, os.path.join(os.path.dirname(__file), renamed)
            )


def onFolder_rename2(folder, newBegin, stripStr, fileFormats=None):
    """
    Erase some characters of file name and add something to the
    begining of the file
    """
    
    files = lst_ff(folder, file_format=fileFormats)
    
    for _file in files:
        name = fprop(_file, 'fn', forceLower=True)
        
        new_name = name.replace(stripStr, '')
        new_name = "{}{}{}".format(newBegin, new_name, fprop(_file, 'ff'))
        
        os.rename(_file, os.path.join(os.path.dirname(_file), new_name))


def rename_mantainid(folder, new_name):
    """
    Rename files mantain integer part

    if new_name = 'dclv'

    a file with a old name like
    filename100_tst.tif

    will have a new name like
    dclv_100.tif
    """

    fs = lst_ff(folder, rfilename=True)

    for f in fs:
        fn, fe = os.path.splitext(f)

        int_v = re.search(r'\d+', fn).group()

        nname = f"{new_name}_{int_v}{fe}"

        os.rename(
            os.path.join(folder, f),
            os.path.join(folder, nname)
        )


"""
Copy Things
"""

def copy_file(src, dest, move=None):
    """
    Copy a file
    """
    
    if not move:
        from shutil import copyfile
    
        copyfile(src, dest)
    
    else:
        from shutil import move as mv

        mv(src, dest)
    
    return dest


"""
Specific Utils to manage data in folders
"""

def identify_groups(folder, splitStr, groupPos, outFolder):
    """
    Identifica o grupo a que um ficheiro pertence e envia-o para uma nova
    pasta com os ficheiros que pertencem a esse grupo.
    
    Como e que o grupo e identificado?
    * O nome do ficheiro e partido em dois em funcao de splitStr;
    * O groupPos identifica qual e a parte (primeira ou segunda) que 
    corresponde ao grupo.
    """
    
    files = lst_ff(folder)
    
    # List groups and relate files with groups:
    groups = {}
    for _file in files:
        # Split filename
        filename = os.path.splitext(os.path.basename(_file))[0]
        fileForm = os.path.splitext(os.path.basename(_file))[1]
        group = filename.split(splitStr)[groupPos]
        namePos = 1 if not groupPos else 0
        
        if group not in groups:
            groups[group] = [[filename.split(splitStr)[namePos], fileForm]]
        else:
            groups[group].append([filename.split(splitStr)[namePos], fileForm])
    
    # Create one folder for each group and put there the files related
    # with that group.
    for group in groups:
        group_folder = mkdir(os.path.join(outFolder, group))
            
        for filename in groups[group]:
            copy_file(
                os.path.join(folder, '{a}{b}{c}{d}'.format(
                    a=filename[0], b=splitStr, c=group,
                    d=filename[1]
                )),
                os.path.join(group_folder, '{a}{b}'.format(
                    a=filename[0], b=filename[1]
                ))
            )

