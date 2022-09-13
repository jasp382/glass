(function () {'use strict';

angular
    .module('jsidejs.services')
    .service('LeafletControls', LeafletControls);

LeafletControls.$inject = [
    'L'
];

function LeafletControls(L) {
    var service = {
        zoomToFullExtent : zoomToExtent,
        positionElements : getPosition,
        changeMapCenter  : ChangeMapCenter,
        activateZoomIn   : activateZoomIn,
        activateZoomOut  : activateZoomOut,
        ActivateDrawBox  : ActivateDrawBox,
        executeZoom      : executeZoom,
        addScale         : addScale,
        putScale         : putScale,
        maxBounds        : maxBounds,
        setMaxBounds     : setMaxBounds,
        toggleSidebar    : toggleSidebar,
        updateSidebarBtn : UpdateSidebarButtons
    };
    
    return service;
    
    /////////////////////////////
    
    function zoomToExtent(scope) {
        return execute;
        
        function execute() {
            if (scope.vm.settings.currentCenter.lat === scope.vm.settings.center.lat
                && scope.vm.settings.currentCenter.lng === scope.vm.settings.center.lng
                && scope.vm.settings.currentCenter.zoom === scope.vm.settings.center.zoom) {
                
                scope.vm.map.setView(
                    new L.LatLng(
                        scope.vm.settings.center.lat,
                        scope.vm.settings.center.lng
                    ),
                    scope.vm.settings.center.zoom
                );
            };
            
            scope.vm.settings.currentCenter = {
                lat: scope.vm.settings.center.lat,
                lng: scope.vm.settings.center.lng,
                zoom: scope.vm.settings.center.zoom
            };
        };
    };
    
    /////////////////////////////
    
    // Change Map Center
    function ChangeMapCenter(scope) {
        return changeMapCenter;
        
        function changeMapCenter() {
            scope.vm.map.setView(
                new L.LatLng(
                    scope.vm.settings.currentCenter.lat,
                    scope.vm.settings.currentCenter.lng
                ),
                scope.vm.settings.currentCenter.zoom
            );
        };
    };
    
    /////////////////////////////
    
    // Put Leaflet Elements and Controls in the Rigth place
    function getPosition(scope) {
        if (scope.vm.settings.position === undefined) {
            scope.vm.scale_pos = 'bottomleft';
            scope.vm.zoom_pos = 'topleft';
            scope.vm.search_pos = 'topleft';
            scope.vm.contents_pos = 'topleft';
            scope.vm.draw_pos = 'topleft';
        } else {
            scope.vm.scale_pos = scope.vm.settings.position.scale === undefined ? 
                'bottomleft' : scope.vm.settings.position.scale;
            
            scope.vm.zoom_pos = scope.vm.settings.position.zoom === undefined ?
                'topleft' : scope.vm.settings.position.zoom;
            
            scope.vm.search_pos = scope.vm.settings.position.search === undefined ?
                'topleft' : scope.vm.settings.position.search;
            
            scope.vm.contents_pos = scope.vm.settings.position.contents === undefined ?
                'topleft' : scope.vm.settings.position.contents;
            
            scope.vm.draw_pos = scope.vm.settings.position.draw === undefined ?
                'topleft' : scope.vm.settings.position.draw;
        }
    };
    
    /////////////////////////////
    
    // Zoom by boundary
    function activateZoomIn(scope) {
        return zoomIn;
        
        function zoomIn() {
            scope.vm.zoom_in  = true;
            scope.vm.zoom_out = false;
        };
    };
    
    function activateZoomOut(scope) {
        return zoomOut;
        
        function zoomOut() {
            scope.vm.zoom_out = true;
            scope.vm.zoom_in = false;
        };
    };
    
    function ActivateDrawBox(scope) {
        return activeDrawBox;
        
        function activeDrawBox() {
            if (!scope.vm.zoom_in && !scope.vm.zoom_out) return;

            if (scope.vm.drawZoom) return;
            
            scope.vm.boxdraw = new L.Draw.Rectangle(
                scope.vm.map,
                {
                    metric: false,
                    feet: false,
                    shapeOptions: {color: 'black'}
                }
            );

            scope.vm.boxdraw.enable();

            scope.vm.drawZoom = true;
        };
    };
    
    function executeZoom(scope, event) {
        scope.vm.zoom_lyr = event.layer;
        scope.vm.drawnItems.addLayer(scope.vm.zoom_lyr);
            
        scope.$apply(function () {
            if (scope.vm.zoom_in && !scope.vm.zoom_out) {
                scope.vm.map.fitBounds(scope.vm.zoom_lyr.getBounds());
            } else if (!scope.vm.zoom_in && scope.vm.zoom_out) {
                var bounds = scope.vm.map.getBounds();
                bounds._northEast.lat = bounds._northEast.lat + 0.3;
                bounds._northEast.lng = bounds._northEast.lng + 0.3;
                bounds._southWest.lat = bounds._southWest.lat - 0.3;
                bounds._southWest.lng = bounds._southWest.lng - 0.3;
                scope.vm.map.fitBounds(bounds);
            };
            scope.vm.zoom_in = false;
            scope.vm.zoom_out = false;
            scope.vm.drawZoom = false;
        });

        scope.vm.drawnItems.removeLayer(scope.vm.zoom_lyr);
    };
    
    /////////////////////////////
    
    function addScale(scope) {
        L.control.scale({ position: scope.vm.scale_pos }).addTo(scope.vm.map);
    };

    function putScale(positionStr, mapObj) {
        L.control.scale({ position: positionStr }).addTo(mapObj);
    }
    
    /////////////////////////////
    
    function maxBounds(scope) {
        if (scope.vm.settings.bounds) {
            scope.vm.map.setMaxBounds(
                L.latLngBounds(
                    L.latLng(scope.vm.settings.bounds.bottom, scope.vm.settings.bounds.left),
                    L.latLng(scope.vm.settings.bounds.top, scope.vm.settings.bounds.right)
                )
            );
        };
    };

    function setMaxBounds(mapObj, boundsObj) {
        if (boundsObj) {
            mapObj.setMaxBounds(L.latLngBounds(
                L.latLng(boundsObj.bottom, boundsObj.left),
                L.latLng(boundsObj.top, boundsObj.right)
            ));
        };
    };
    
    /////////////////////////////
    
    // Function to control table of contents (sidebar)
    function toggleSidebar(mapElm, scope) {
        return showTableContents;
        
        function showTableContents(status) {
            if (status) {
                angular.element(mapElm).removeClass(scope.vm.sidebar.show);
                angular.element(mapElm).addClass(scope.vm.sidebar.hide);

                scope.vm.insertInputs = false;
                scope.vm.settings.sidebar_btn.form = false;
                scope.vm.lyrTree = false;
                scope.vm.settings.sidebar_btn.tbl_content = false;
            } else {
                angular.element(mapElm).removeClass(scope.vm.sidebar.hide);
                angular.element(mapElm).addClass(scope.vm.sidebar.show);

                scope.vm.insertInputs = true;
                scope.vm.settings.sidebar_btn.form = true;
                scope.vm.lyrTree = false;
                scope.vm.settings.sidebar_btn.tbl_content = false;
            }
            
            scope.vm.sidebar.sidebar ^= true;
            
            scope.vm.map.invalidateSize();
        };
    };
    
    function UpdateSidebarButtons(scope) {
		return updateSidebar;
		
		function updateSidebar() {
			if (!scope.vm.sidebar.sidebar) return;
			
			var searchIcon = angular.element( document.querySelector( '#searchIcon' ) ),
            	editIcon   = angular.element( document.querySelector( '#editIcon' ) );

			if (scope.vm.insertInputs) {
				searchIcon.css('background-color', 'white');
				editIcon.css('background-color', '#2C709F');
			} else {
				searchIcon.css('background-color', '#2C709F');
				editIcon.css('background-color', 'white');
			}
		}
	}
};

})();