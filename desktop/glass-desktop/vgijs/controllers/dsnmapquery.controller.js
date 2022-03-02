(function () {'use strict';

angular
    .module('vgijs.controllers')
    .controller('DsnMapSearchController', DsnMapSearchController);

DsnMapSearchController.$inject = [
    '$scope', '$routeParams', '$location',
    'LeafletLayers', 'deviceDetector', '$window'
];

function DsnMapSearchController(
                              $scope,
                              $routeParams,
                              $location,
                              LeafletLayers,
                              deviceDetector, $window) {
    var mapVm = this;
    
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
    };
    
    // Are there some data from the search for VGI?
    mapVm.status = thereIsData($location.absUrl());
    
    function thereIsData (url) {
        if (url.indexOf('status=201') > -1) {
            var thereAreData = 201;
        } else if (url.indexOf('status=202') > -1) {
            var thereAreData = 202;
        } else {
            var thereAreData = 200;
        }

        return thereAreData;
    }

    mapVm.notShow = function() {
        mapVm.status = 3;
    };
    
    // Main map characteristics and settings
    mapVm.settings = {
    	service : 'search',
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
            zoom: 'topleft'
        },
        draw: {
        	func   : 'circulus',
            edit   : false,
            output : 'default',
            delet  : false,
            radius : undefined
        },
        sidebar_btn: {
            form: true,
            tbl_content: false
        },
        text : {
        	keyword     : undefined,
        	datasources : ''
        }
    };
    
    // Avoid errors related with the non-utilization of the cells feature
    mapVm.cells = undefined;

    // Delete drawed elements
    mapVm.delDrawed = function () {
        mapVm.settings.draw.delet = true;
    };
    
    // Show table of contents if there are data
    $scope.$watch('mapVm.status', showLayerTree, true);
    
    function showLayerTree() {
    	if (mapVm.status === 201 || mapVm.status === 202) {
    		mapVm.settings.sidebar_btn.form = false;
    		mapVm.settings.sidebar_btn.tbl_content = true;
    	}
    }
}

})();