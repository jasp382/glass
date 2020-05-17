"""
Delete Layers
"""

from django.http import HttpResponseRedirect


def del_indicatorlyr(request, lyr_id):
    """
    Delete Layer
    """
    
    from wgeng.settings        import DATABASES, GEOSERVER_SET
    from weapi.models          import LyrIndicators
    from gasp3.sql.mng.tbl     import del_tables
    from gasp3.web.geosrv.styl import del_style
    from gasp3.web.geosrv.lyrs import del_lyr
    
    STYLE = "style_{}".format(str(lyr_id))
    LYR   = ["lyr_{}".format(str(lyr_id)),"det_{}".format(str(lyr_id))]
    
    l = lyr.objects.get(fid=int(lyr_id))
    
    l.delete()
    
    for ly in LYR:
        # Delete View
        del_tables(DATABASES['default'], ly, isViews=True)
        # Delete Layer in Geoserver
        del_lyr(ly, conf=GEOSERVER_SET)
    
    # Delete Style
    del_style(STYLE, conf=GEOSERVER_SET)
    
    return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/')


def delpntlyr(request, lyrid):
    """
    Delete Point Layer
    """
    
    from wgeng.settings        import DATABASES, GEOSERVER_SET
    from weapi.models          import PntLyr
    from gasp3.sql.mng.tbl     import del_tables
    from gasp3.web.geosrv.lyrs import del_lyr
    
    LN = "pnt_{}".format(lyrid)
    del_lyr(LN, conf=GEOSERVER_SET)
    del_tables(DATABASES['default'], LN, isViews=True)
    
    l = PntLyr.objects.get(fid=int(lyrid))
    l.delete()
    
    return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/')


def delpolylyr(request, lyrid):
    """
    Delete Polygon Layer
    """
    
    from wgeng.settings import DATABASES
    from weapi.models import PolygonLyr
    
    l = PolygonLyr.objects.get(fid=int(lyrid))
    l.delete()
    
    return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/')

