(function () {"use strict";

angular
	.module('vgijs.directives')
	.directive('vgijsFirelocReport', firelocReport);

firelocReport.$inject = ['BASEMAPS_TREE', 'LeafletLayers', '$window', 'API_URL'];

function firelocReport(BASEMAPS_TREE, LeafletLayers, $window, API_URL) {
	var directive = {
		restrict     : 'E',
		replace      : false,
		transclude   : true,
		templateUrl  : '/static/vgi-angular/firelocReport.html',
		scope        : {
			settings : '=',
		},
		link         : link,
		controller   : firelocReportController,
		controllerAs : 'vm',
		bindToController : true
	};
	
	return directive;
	
	function link(scope, iElement, iAttrs) {
		scope.vm.api_url = API_URL;
		
		// Get id for the map
		var mapElm = iElement[0].children[1];
		
		// Leaflet map initialization
		scope.vm.map = L.map(mapElm).fitWorld();
		
		/////////////////////////   Basemaps Control   /////////////////////////

		// Add basemap to the map
		// Basemaps tree
		scope.vm.basemaps = BASEMAPS_TREE;
		
		scope.vm.changeBasemap = LeafletLayers.getBasemapName(scope);
		
		scope.vm.basemap = "MAPBOX_STREETS";
		
		scope.$watch(
			'vm.basemap', LeafletLayers.changeBasemap(scope), true
		);
		
		scope.vm.map.locate({setView: true, maxZoom: 16});

		///////////////////////////   End Section   ////////////////////////////
		
		// Get User position
		scope.vm.notPosition = true;
		function onLocationFound(e) {
			scope.$apply(function () {
				scope.vm.settings.form.latlng = String(e.latlng.lat)
					+ ';' + String(e.latlng.lng);
			});
			
			scope.vm.notPosition = false;
			L.marker(e.latlng).addTo(scope.vm.map);
		};
		
		scope.vm.map.on('locationfound', onLocationFound);
		
		// Map Position warning
		scope.vm.showWarning = true;
		
		scope.vm.hideWarning = function () {
			scope.vm.showWarning = false;
		};
		
		// Control form showing;
		scope.vm.showInit    = true;
		scope.vm.showMap     = false;
		scope.vm.showForm    = false;
		scope.vm.showImg     = false;
		scope.vm.isUpload    = false;
		scope.vm.showCompass = false;
		scope.vm.showText    = false;
		
		// Show Map
		scope.vm.ttShowMap = function () {
			scope.vm.showInit = false;
			scope.vm.showMap  = true;
		};
		
		scope.vm.nextForm = function () {
			if (scope.vm.showMap) {
				scope.vm.showMap = false;
				scope.vm.showForm = true;
				scope.vm.showCompass = true;
			} else if (scope.vm.showCompass) {
				scope.vm.showCompass = false;
				scope.vm.showImg = true;
			}
		};
		
		// The user uploaed something
		scope.vm.isUploadTrue = function () {
			scope.$apply(function () {
				scope.vm.isUpload =true;
			});
		}
		
		// Direction Control
		scope.vm.isAbsolute = undefined;
		scope.vm.gamma = undefined;
		scope.vm.beta = undefined;
		scope.vm.north_direction = -9999;
		scope.vm.cell_direction  = -9999;
		scope.vm.needCalibration = undefined;
		
		scope.vm.final_north = 999;
		scope.vm.final_cell  = 999;
		scope.vm.final_beta  = 999;
		scope.vm.final_gama  = 999;
		
		if ('DeviceOrientationEvent' in window) {
			$window.addEventListener('deviceorientation', deviceOrientation, true);
			$window.addEventListener(
				'deviceorientationabsolute', deviceOrientationAbsolute, true
			);
		} else {
			scope.vm.north_direction = false;
			scope.vm.cell_direction  = false;
		}
		
		function deviceOrientation(eventData) {
			scope.$apply(function () {
				scope.vm.cell_direction = parseInt(eventData.alpha);
				scope.vm.cell_direction = !scope.vm.cell_direction ? 999 : scope.vm.cell_direction;
			})
		}
		
		function deviceOrientationAbsolute(eventData) {
			scope.$apply(function () {
				scope.vm.north_direction = parseInt(eventData.alpha);
				scope.vm.isAbsolute = eventData.absolute;
				scope.vm.beta = parseInt(eventData.beta);
				scope.vm.gamma = parseInt(eventData.gamma);
				
				scope.vm.north_direction = !scope.vm.north_direction ? 999 : scope.vm.north_direction;
				scope.vm.beta = !scope.vm.beta ? 999 : scope.vm.beta;
				scope.vm.gamma = !scope.vm.gamma ? 999 : scope.vm.gamma;
			})
		}
		
		if ('oncompassneedscalibration' in window) {
			$window.addEventListener('compassneedscalibration', youNeedCalibration, true);
		} else {
			scope.vm.needCalibration = 2;
		}
		
		function youNeedCalibration (event) {
			scope.$apply(function () {
				scope.vm.needCalibration = 1;
			})
		}
		
		// North Value to Form
		scope.vm.setNorth = function() {
			scope.vm.final_north = scope.vm.north_direction;
			scope.vm.final_cell  = scope.vm.cell_direction;
			scope.vm.final_beta  = scope.vm.gamma;
			scope.vm.final_gama  = scope.vm.beta;
		}
	};
}

firelocReportController.$inject = ['$scope'];

function firelocReportController($scope) {
	/* jshint validthis: true */
	var vm = this;
}

})();