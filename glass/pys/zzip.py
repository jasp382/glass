"""
Compress files with Python
"""


def tar_compress_folder(tar_fld, tar_file):
    """
    Compress a given folder
    """
    
    import os
    from glass.pys  import execmd
    
    cmd = (
        f'cd {str(os.path.dirname(tar_fld))} && tar -czvf '
        f'{tar_file} {str(os.path.basename(tar_fld))}'
    )
    
    code, out, err = execmd(cmd)
    
    return tar_file


def zip_files(lst_files, zip_file):
    """
    Zip all files in the lst_files
    """
    
    import zipfile
    import os
    
    __zip = zipfile.ZipFile(zip_file, mode='w')
    
    for f in lst_files:
        __zip.write(f, os.path.relpath(f, os.path.dirname(f)),
                    compress_type=zipfile.ZIP_DEFLATED)
    
    __zip.close()

    return zip_file


def zip_folder(folder, zip_file):
    from glass.pys.oss import lst_ff
    
    files = lst_ff(folder)
    
    zip_files(files, zip_file)



def unzip(zipf, destination):
    """
    Unzip some zip file
    """

    from glass.pys import execmd

    execmd(f"unzip {zipf} -d {destination}")

    return destination



def pyunzip(zipf, destination):
    """
    Unzip file using zipfile package
    """

    import os
    from zipfile import ZipFile

    ff = []
    with ZipFile(zipf, 'r') as zipo:
        zipff = zipo.namelist()

        for f in zipff:
            zipo.extract(f, destination, pwd=None)

            ff.append(os.path.join(destination, f))

    return ff

