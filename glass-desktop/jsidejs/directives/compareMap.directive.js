(function () {"use strict";

angular
	.module('jsidejs.directives')
	.directive('mappingCompare', mappingCompare);

mappingCompare.$inject = [
	'L', '$window', '$http', 'LeafLayers', 'LeafletControls', 'BASEMAPS_TREE'
];

function mappingCompare(L, $window, $http, LeafLayers, LeafletControls,
	BASEMAPS_TREE) {
	var directive = {
		restrict         : 'E',
		replace          : false,
		transclude       : true,
		templateUrl      : '/static/maps-compare.html',
		scope : {
			caseid  : '=',
			ctop    : '=',
			cbottom : '=',
			cleft   : '=',
			cright  : '='
		},
		link             : link,
		controller       : mappingCompareController,
		controllerAs     : 'vm',
		bindToController : true
	};

	return directive;

	function link(scope, iElement, iAttrs) {
		// Get id for the map
		var leftMap  = iElement[0].children[0].children[2],
			rightMap = iElement[0].children[1].children[2];

		/////////////////////////   Map Initialization   ///////////////////////
		// Main map characteristics and settings
		scope.vm.settings = {
			center : {
				lat  : undefined,
				lng  : undefined,
				zoom : undefined
			},
			extent : L.latLngBounds(
				L.latLng(scope.vm.ctop, scope.vm.cleft),
				L.latLng(scope.vm.cbottom, scope.vm.cright)
			),
			scale : true,
			zoom : {
				min : 6,
				max : 20
			},
			bounds: {
				top    : scope.vm.ctop,
				right  : scope.vm.cright,
				bottom : scope.vm.cbottom,
				left   : scope.vm.cleft
			},
			position : {
				scale : 'bottomright',
				zoom  : 'topleft'
			}
		};

		// Left Map
		scope.vm.leftMap = L.map(leftMap, {
			minZoom     : scope.vm.settings.zoom.min,
			maxZoom     : scope.vm.settings.zoom.max,
			zoomControl : false,
			scale       : scope.vm.settings.scale
		});

		// Right Map
		scope.vm.rightMap = L.map(rightMap, {
			minZoom     : scope.vm.settings.zoom.min,
			maxZoom     : scope.vm.settings.zoom.max,
			zoomControl : false,
			scale       : scope.vm.settings.scale
		});

		scope.vm.leftMap.fitBounds(scope.vm.settings.extent);
		scope.vm.rightMap.fitBounds(scope.vm.settings.extent);

		scope.vm.settings.center.lat = scope.vm.leftMap.getCenter().lat;
		scope.vm.settings.center.lng = scope.vm.leftMap.getCenter().lng;
		scope.vm.settings.center.zoom = scope.vm.leftMap.getZoom();

		// Give position to things
		LeafletControls.positionElements(scope);

		// Add Scale to the Map
		LeafletControls.putScale(scope.vm.settings.position.scale, scope.vm.leftMap);
		LeafletControls.putScale(scope.vm.settings.position.scale, scope.vm.rightMap);

		// Set Maximum bounds
		LeafletControls.setMaxBounds(scope.vm.leftMap, scope.vm.settings.bounds);
		LeafletControls.setMaxBounds(scope.vm.rightMap, scope.vm.settings.bounds);

		/////////////////////////   Basemaps Control   /////////////////////////
		// Default basemap
		scope.vm.leftBasemapLyr  = undefined;
		scope.vm.rightBasemapLyr = undefined;
		
		scope.$watch('vm.leftBasemapLyr', LeafLayers.setBasemapOnMap(
			scope.vm.leftMap, scope.vm.leftBasemapLyr,
			scope.vm.settings.zoom.max
		), true);

		scope.$watch('vm.rightBasemapLyr', LeafLayers.setBasemapOnMap(
			scope.vm.rightMap, scope.vm.rightBasemapLyr,
			scope.vm.settings.zoom.max
		), true);

		//////////////////////////   Zoom Control   ///////////////////////////
		
		// Change view center
		scope.vm.settings.currentCenter = {
			lat  : scope.vm.settings.center.lat,
			lng  : scope.vm.settings.center.lng,
			zoom : scope.vm.settings.center.zoom
		};
		
		// Zoom to full extent
		scope.vm.zoomToFullExtent = LeafletControls.zoomToFullExtent(scope);
		
		// Zoom by boundary
		scope.vm.zoom_in         = false;
		scope.vm.zoom_out        = false;
		scope.vm.drawZoom        = false;
		scope.vm.activateZoomIn  = LeafletControls.activateZoomIn(scope);
		scope.vm.activateZoomOut = LeafletControls.activateZoomOut(scope);
		
		scope.$watchCollection(
			'[vm.zoom_in, vm.zoom_out]',
			LeafletControls.ActivateDrawBox(scope), true
		);
		
		scope.$watchCollection(
			'[vm.zoom_in, vm.zoom_out]', changeColor, true
		);
		
		function changeColor (current) {
			var currentZoomIn  = current[0],
				currentZoomOut = current[1],
				zoomInElem  = angular.element( document.querySelector( '#zoom-in' ) ),
				zoomOutElem = angular.element( document.querySelector( '#zoom-out' ) );
			
			if (currentZoomIn && !currentZoomOut) {
				zoomInElem.css('background-color', '#06b4d1');
				zoomOutElem.css('background-color', '#e0e0eb');
			} else if (!currentZoomIn && currentZoomOut) {
				zoomInElem.css('background-color', '#e0e0eb');
				zoomOutElem.css('background-color', '#06b4d1');
			} else if (!currentZoomIn && !currentZoomOut) {
				zoomInElem.css('background-color', '#e0e0eb');
				zoomOutElem.css('background-color', '#e0e0eb');
			} else {
				return;
			}
		};
		
		//////////////////////////  Draw Section   ///////////////////////////
		
		// Deal with drawed objects
		/*
		scope.vm.drawnItems = L.featureGroup().addTo(scope.vm.map);
		
		scope.vm.map.on(L.Draw.Event.CREATED, function(event) {
			LeafletControls.executeZoom(scope, event);
		});*/

		//////////////////////////  Layer Control  ///////////////////////////
		scope.vm.lyrLeft = {};
		scope.vm.lyrRight = {};
		scope.vm.lyrListLeft = undefined;
		scope.vm.lyrListRight = undefined;
		scope.vm.leftYear = undefined;
		scope.vm.rightYear = undefined;
		scope.vm.newLeftLayer = undefined;
		scope.vm.newRightLayer = undefined;
		scope.vm.currentLeftLayer = undefined;
		scope.vm.currentRightLayer = undefined;
		scope.vm.leftLegend = undefined;
		scope.vm.rightLegend = undefined;

		scope.$watch('vm.lyrLeft', LeafLayers.obtainLyrByYear(
			scope.vm.lyrLeft, scope.vm.caseid), true);
		
		scope.$watch('vm.lyrRight', LeafLayers.obtainLyrByYear(
			scope.vm.lyrRight, scope.vm.caseid), true);
		
		scope.$watch('vm.leftYear', setLeftLyr, true);
		scope.$watch('vm.rightYear', setRightLyr, true);

		function setLeftLyr() {
			if (!scope.vm.leftYear) return;

			scope.vm.lyrListLeft = scope.vm.lyrLeft[scope.vm.leftYear];
		};

		function setRightLyr() {
			if (!scope.vm.rightYear) return;

			scope.vm.lyrListRight = scope.vm.lyrRight[scope.vm.rightYear];
		};

		scope.$watch('vm.newLeftLayer', addLeftLyr, true);

		function addLeftLyr () {
			if (!scope.vm.newLeftLayer) return;

			if (scope.vm.currentLeftLayer) {
				scope.vm.leftMap.removeLayer(scope.vm.currentLeftLayer);
			};

			var lyr = scope.vm.lyrListLeft[Number(scope.vm.newLeftLayer)];

			scope.vm.currentLeftLayer = L.tileLayer.wms(lyr.url, {
				layers : lyr.dname,
				transparent : true,
				format : 'image/png',
				styles : lyr.style
			});
			scope.vm.leftMap.addLayer(scope.vm.currentLeftLayer);
			scope.vm.leftLegend = lyr.lyr_cls;
			scope.vm.leftName = lyr.name;
		};

		scope.$watch('vm.newRightLayer', addRightLyr, true);

		function addRightLyr () {
			if (!scope.vm.newRightLayer) return;

			if (scope.vm.currentRightLayer) {
				scope.vm.rightMap.removeLayer(scope.vm.currentRightLayer);
			};

			var lyr = scope.vm.lyrListRight[Number(scope.vm.newRightLayer)];

			scope.vm.currentRightLayer = L.tileLayer.wms(lyr.url, {
				layers : lyr.dname,
				transparent : true,
				format : 'image/png',
				styles : lyr.style
			});
			scope.vm.rightMap.addLayer(scope.vm.currentRightLayer);
			scope.vm.rightLegend = lyr.lyr_cls;
			scope.vm.rightName = lyr.name;
		};

	};
};

mappingCompareController.$inject = ['$scope'];

function mappingCompareController($scope) {
	/* jshint validthis: true */
	var vm = this;
}
})();