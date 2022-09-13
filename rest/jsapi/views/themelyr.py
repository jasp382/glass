"""
Manage Theme Layers in WebGIS Engine
"""

from django.http                  import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework               import generics

from weapi.models import ThemeLyr
from weapi.serial.lstindicator import ListIndicators
class IndicatorsView(generics.ListAPIView):
    queryset = ThemeLyr.objects.all()
    serializer_class = ListIndicators


@csrf_exempt
def receive_themelyr(request):
    """
    Receive an Indicator
    """
    
    if request.method == 'POST':
        from weapi.utils         import get_rqst_id
        from gasp3.web.djg.mdl.w import update_model
        
        rqst = get_rqst_id(request)
        slug = request.POST['slug-indicator']
        name = request.POST['name-indicator']
        unit = request.POST['unit-indicator']
        
        update_model('atlas.models.theme_lyr', [{
            'fid'  : rqst,
            'slug' : slug,
            'name' : name,
            'unit' : unit
        }])
        
        return HttpResponseRedirect('/pt/atlas/lyr-themes/manage/?status=201')
    
    else:
        return HttpResponseRedirect('/pt/atlas/lyr-themes/manage/')


def del_themelyr(request, lyr_id):
    """
    Delete indicator
    """
    
    from weapi.models import theme_lyr
    
    inst = theme_lyr.objects.get(fid=int(lyr_id))
    
    inst.delete()
    
    return HttpResponseRedirect('/pt/atlas/lyr-themes/manage/?status=202')


@csrf_exempt
def receive_multitheme(request):
    """
    Receive a table with indicators names
    """
    
    if request.method == 'POST':
        import os
        from atlas               import DATA_FOLDER
        from atlas.utils         import get_rqst_id
        from gasp3.web.djg.ff    import save_file
        from gasp3.pyt.oss       import create_folder
        from gasp3.pyt.ff.fld    import cols_xlsx
        from gasp3.web.djg.mdl.w import update_model
        
        # Get Files from POST 
        files = request.FILES.getlist('new-themes')
        
        rqst = get_rqst_id(request)
        
        # Save file
        fld = create_folder(os.path.join(DATA_FOLDER, str(rqst)))
        tbl = save_file(fld, files[0])
        
        # Get columns in file
        cols = cols_xlsx(tbl, sheet=None)
        
        # Updata data table
        update_model('atlas.models.upload_data', [{
            'fid'      : rqst,
            'filename' : os.path.basename(tbl),
            'utiliza'  : 1
        }])
        
        # Update Columns Name
        from atlas.models import upload_data
        inst = upload_data.objects.get(fid=int(rqst))
        update_model('atlas.models.upload_cols', [{
            'fid'      : int("{}{}".format(str(rqst), str(idx))),
            'rqst_id'  : inst,
            'idx_col'  : idx,
            'name_col' : cols[idx],
            'ctx_col'  : False
        } for idx in range(len(cols))])
        
        return HttpResponseRedirect(
            '/pt/atlas/lyr-themes/manage/?status=203&rqst_id={}'.format(
                str(rqst)
            ))
    
    else:
        return HttpResponseRedirect('/pt/atlas/lyr-themes/manage/')


@csrf_exempt
def receive_multitheme2(request):
    """
    Data in table with indicators name to database
    """
    
    if request.method == 'POST':
        import os
        from wgeng.settings import DATABASES
        from atlas          import DATA_FOLDER
        from gasp3.fm       import tbl_to_obj
        from gasp3.sql.to   import df_to_db
        
        # Get Parameters from FORM
        rqst  = request.POST['rqst-fid']
        name  = request.POST['col-name']
        slug  = request.POST['col-slug']
        unit  = request.POST['col-unit']
        fname = request.POST['file-name']
        
        # File to Dataframe
        TBL_PATH = os.path.join(DATA_FOLDER, str(rqst), fname)
        df = tbl_to_obj(TBL_PATH)
        
        # Rename Columns
        df.rename(columns={
            name : 'name', slug : 'slug', unit : 'unit'
        }, inplace=True)
        
        cols = ['name', 'slug', 'unit']
        delCols = [c for c in df.columns.values if c not in cols]
        df.drop(delCols, axis=1, inplace=True)
        
        # Add FID Col
        FID_N = int("{}0".format(str(rqst)))
        df["fid"] = df.index + FID_N
        
        # Slice slug
        df["slug"] = df.slug.str.slice(stop=10)
        
        # Data to DB
        df_to_db(DATABASES['default'], df, 'weapi_themelyr', append=True)
        
        return HttpResponseRedirect(
            '/pt/atlas/lyr-themes/manage/?status=204'
        )
    
    else:
        return HttpResponseRedirect('/pt/atlas/lyr-themes/manage/')

