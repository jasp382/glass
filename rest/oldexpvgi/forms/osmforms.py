from django import forms

class OsmToLulc_FrstPhase(forms.Form):
    """
    Code example (if we want to change widget attributes)
        
    def __init__(self, *args, **kwargs):
        super(DrawBoundaryForm, self).__init__(*args, **kwargs)
        self.fields['draw_boundary'].widget.attrs.update({'ng-model': 'mapVm.forms.osmtolulc.draw_out'})
    """

class OsmtolulcFile(forms.Form):
    """
    OSM TO LULC ALGORITHM Upload File form
    """
    
    shp_file = forms.FileField(
        label='Upload your Area Boundary File',
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple' : True})
    )
    
    epsg = forms.CharField(
        label='EPSG code (use only projected systems):',
        max_length=10, initial='3857'
    )
    

class OsmtolulcExtent(forms.Form):
    """
    OSM TO LULC ALGORITHM define extent
    """
    
    top    = forms.CharField(label='TOP: '   )
    right  = forms.CharField(label='RIGHT: ' )
    bottom = forms.CharField(label='BOTTOM: ')
    left   = forms.CharField(label='LEFT: '  )
    
    epsg = forms.CharField(
        label='EPSG code (use only projected systems):',
        max_length=10
    )


class OsmtolulcDraw(forms.Form):
    """
    OSM TO LULC ALGORITHM draw a bounding box
    """
    
    form_type = forms.CharField(initial='draw_bb')
    
    draw_rectangle = forms.CharField(required=True)
    
    phase = forms.CharField(initial='down-phase')


class OsmtolulcRun(forms.Form):
    """
    OSM TO LULC ALGORITHM run procedure
    """
    
    nomenclature = forms.CharField(
        max_length=20
    )
    
    rqst  = forms.CharField(max_length=20)
    phase = forms.CharField(initial='lulc-phase')


class OsmToLulc_SecPhase(forms.Form):
    nomenclature = forms.ChoiceField(
        choices=(
            ('URBAN_ATLAS', 'Urban Atlas'),
            ('CORINE_LAND_COVER','Corine Land Cover'),
            ('GLOBE_LAND_30', 'Globe Land 30')
        ),
        label='Nomenclature to use:',
    )
    
    osm_upload_file = forms.FileField(
        required=False,
        label='OSM file for upload:',
        widget=forms.ClearableFileInput(attrs={'multiple': True})
    )
    
    request_id = forms.CharField(
        widget=forms.HiddenInput(), 
        max_length=20
    )


"""
Example code to see how to define onChange 


class OsmToShp_Main(forms.Form):
    osm_file = forms.ChoiceField(
        choices=(
            ('DEFAULT', ''),
            ('UPLOAD_A_FILE', 'Upload an OSM File'),
            ('DO_NOT_UPLOAD_A_FILE', 'Do not upload an OSM File')
        ),
        label='OpenStreetMaps pbf/xml file:',
        widget=forms.Select(attrs={"onChange":'refresh_form()'})
    )
"""
    

class OsmToShpForm(forms.Form):
    osm_file = forms.FileField(
        label='OSM file for upload:', required=False
    )
    
    boundary_file = forms.FileField(
        label='Study Area Boundary:',
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False
    )
    
    boundary_draw = forms.CharField()
    
    epsg = forms.CharField(
        label='EPSG Code:', max_length=10, initial='3857'
    )


class OsmDownloadBoundary(forms.Form):
    
    boundary = forms.FileField(
        label='Study Area Boundary:',
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False
    )
    
    draw_boundary = forms.CharField(required=False)
    
    epsg = forms.CharField(
        label='EPSG Code:', max_length=10, initial='3857',
        required=False
    )
    
  