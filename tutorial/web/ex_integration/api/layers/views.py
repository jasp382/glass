# REST Framework Dependencies

from rest_framework.response import Response
from rest_framework          import status
from rest_framework.parsers  import JSONParser
from rest_framework          import generics

from layers.models import Layers
from layers.srl import LayersSrl


class ManLayers(generics.GenericAPIView):
    """
    Manage Existing Layers

    GET | List all layers
    POST | Add new layer
    DELETE | Delete all layers
    """

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET | Retrieve all layers and their
        attributes
        """

        lyrs = Layers.objects.all()
        srl = LayersSrl(lyrs, many=True)

        rsp = Response(srl.data, status=status.HTTP_200_OK)

        return rsp
    
    def post(self, request):
        """
        Method POST | Add new layer
        """

        d = request.data

        d["style"] = None

        srl = LayersSrl(data=d)

        if srl.is_valid():
            srl.save()

            response = srl.data
            http = status.HTTP_201_CREATED
        
        else:
            response = {"errors" : str(srl.errors)}
            http = status.HTTP_400_BAD_REQUEST
        
        rsp = Response(response, status=http)

        return rsp
    
    def delete(self, request):
        """
        Method DELETE | Delete all layers
        """

        Layers.objects.all().delete()

        response = {'status' : 'All Layers were deleted'}

        rr = Response(response, status.HTTP_200_OK)

        return rr


class ManLayer(generics.GenericAPIView):
    """
    Manage a specific Layer

    * GET | Retrieves one layer by ID
    * PUT | Updates one layer
    * DELETE | Deletes one layer
    """

    parser_classes = [JSONParser]

    def get(self, request, lid):
        """
        GET - Retrieve a layer by id
        """

        _status, http = None, None

        try:
            lyr = Layers.objects.get(pk=int(lid))
        
        except Layers.DoesNotExist:
            _status, http = {
                "message" : "Layer doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = LayersSrl(lyr)

            response, http = srl.data, status.HTTP_200_OK
        
        else:
            response = _status
        
        rr = Response(response, status=http)

        return rr
    
    def put(self, request, lid):
        """
        PUT - Update existing layer
        """

        _status, http = None, None
        d = request.data

        try:
            lyr = Layers.objects.get(pk=int(lid))
            slyr = LayersSrl(lyr)
            lyrd = slyr.data
        
        except Layers.DoesNotExist:
            _status, http = {
                "message" : "Layer doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            for k in lyrd:
                if k not in d:
                    d[k] = lyrd[k]
            
            srl = LayersSrl(lyr, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                http = status.HTTP_201_CREATED
        
            else:
                response = str(srl.errors)
                http = status.HTTP_400_BAD_REQUEST
        
        else:
            response = _status
        
        rr = Response(response, status=http)

        return rr
    
    def delete(self, request, lid):
        """
        Method DELETE | Delete a specific Layer
        """

        _status, http = None, None

        try:
            lyr = Layers.objects.get(pk=int(lid))
        
        except Layers.DoesNotExist:
            _status, http = {
                "message" : "Layer doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            lyr.delete()

            response = {'status' : 'All Layers were deleted'}
            http = status.HTTP_200_OK
        
        else:
            response = _status
        
        rr = Response(response, status=http)

        return rr


