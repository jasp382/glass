(function () {'use strict';

angular
    .module('vgijs.controllers')
    .controller('OsmMapController', OsmMapController);

OsmMapController.$inject = [
    '$scope', '$routeParams', '$location', 'BASEMAP_OPTIONS',
    'LeafletLayers', '$window', 'deviceDetector'
];

function OsmMapController(
		$scope, $routeParams, $location,
		BASEMAP_OPTIONS, LeafletLayers,
		$window, deviceDetector) {
    var __URL = $location.absUrl(),
		_URL  = new URL($location.absUrl()),
		mapVm = this;
    
    mapVm.goBack = function () {
    	$window.history.back();
    };
    
    mapVm.browser = deviceDetector.browser;
    
    if (mapVm.browser !== 'chrome') {
    	$window.location.href = '/expvgi/?browser=1'
    };
    
    // Manage PopUp
    mapVm.popup = true;
    mapVm.togglePopup = function() {
    	mapVm.popup = false;
    }
    
    mapVm.notShow = function() {
    	mapVm.thereAreData = 3;
    };
    
    function thereIsBB(url) {
    	if (url.indexOf('bb=1') > -1) {
    		var servName = 'osm2lulc_s';
    	} else {
    		var servName = 'osm2lulc_f';
    	}
    	
    	return servName;
    };
    
    function thereIsLegend(url) {
    	var nom = undefined;
    	if (url.indexOf('nomenclature=') > -1) {
    		var get_params = url.split('?')[1];
    		var _get_params = get_params.split('&');
    		
    		_get_params.forEach(function (d) {
    			var name_value = d.split('=');
    			if (name_value[0]  === 'nomenclature') {
    				nom = name_value[1];
    			} else {
    				nom = nom ? nom : undefined;
    			};
    		});
    	} else {
    		nom = '';
    	};
    	
    	return nom;
    }
    
    // Main map characteristics and settings
    mapVm.settings = {
    	service : thereIsBB(__URL),
        center: {
            lat: 39.6818,
            lng: -7.96643,
            zoom: 3
        },
        scale: true,
        zoom: {
            min: 1,
            max: 20
        },
        position: {
            scale: 'bottomright',
            zoom: 'topleft',
        },
        draw: {
        	edit   : false,
            output : 'default',
            func   : 'rectangulus',
            delet  : false
        },
        sidebar_btn: {
        	form       : true,
        	tbl_content: false
        },
        nomenclature : '',
        legend : thereIsLegend(__URL)
    };
    
    // Delete drawed elements
    mapVm.delDrawed = function () {
    	mapVm.settings.draw.delet = true;
    };
    
    // We have data to show?
    mapVm.status = thereIsData($location.absUrl());
    
    function thereIsData (url) {
    	if (url.indexOf('status=101') > -1) {
    		var thereAreData = 101;
    	} else if (url.indexOf('status=102') > -1) {
    		var thereAreData = 102;
    	} else if (url.indexOf('status=103') > -1) {
    		var thereAreData = 103;
		} else if (url.indexOf('status=105') > -1) {
			var thereAreData = 105;
    	} else {
    		var thereAreData = 100;
    	}
    	
    	return thereAreData;
    };
    
    // Show table of contents if there are data
    $scope.$watch(
    	'mapVm.thereAreData', showLayerTree(), true
    );
    
    function showLayerTree() {
    	if (mapVm.status === 105) {
    		mapVm.settings.sidebar_btn.form = false;
    		mapVm.settings.sidebar_btn.tbl_content = true;
    	}
    }
}

})();