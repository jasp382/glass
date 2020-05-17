(function () {"use strict";

angular
	.module('vgijs.directives')
	.directive('vgijsLeafletMapping', leafletMapping);

leafletMapping.$inject = [
	'$window',
	'BASEMAPS_TREE',
	'LeafletLayers',
	'LeafletControls',
	'LeafletDraw'
];

function leafletMapping($window, BASEMAPS_TREE, LeafletLayers, LeafletControls,
		LeafletDraw) {
	var directive = {
		restrict     : 'E',
		replace      : false,
		transclude   : true,
		templateUrl  : '/static/vgi-angular/leafletMainMapping.html',
		scope        : {
			settings  : '=',
			rqstid    : '=',
			servname  : '=',
			bmdefault : '='
		},
		link         : link,
		controller   : LeafletMappingController,
		controllerAs : 'vm',
		bindToController: true
	};

	return directive;

	function link(scope, iElement, iAttrs) {
		// Get id for the map
		var mapElm = iElement[0].firstChild;

		// initial css class for the map
		angular.element(mapElm).addClass('map-with-sidebar');

		// Layers About
		scope.vm.lyrParam = undefined;

		///////////////////////   Sidebar Control   ///////////////////////

		// Change css of the map when the table of contents is hidden
		scope.vm.sidebar = {
			show: 'map-with-sidebar',
			hide: 'map-full-page',
			sidebar: true
		};

		scope.vm.showSidebar = LeafletControls.toggleSidebar(mapElm, scope);

		scope.vm.insertInputs = scope.vm.settings.sidebar_btn.form ? true : false;
		scope.vm.lyrTree = scope.vm.settings.sidebar_btn.tbl_content ? true : false;
		
		angular.element(document).ready(function() {
			var searchIcon = angular.element ( document.querySelector( '#searchIcon' ) ),
				editIcon   = angular.element ( document.querySelector( '#editIcon' ) );
			
			if (scope.vm.insertInputs) {
				searchIcon.css('background-color', 'white');
				editIcon.css('background-color', '#2C709F');
			} else {
				searchIcon.css('background-color', '#2C709F');
				editIcon.css('background-color', 'white');
			};
		});
		
		scope.vm.sideBtnToggle = function () {
			scope.vm.insertInputs ^= true;
			scope.vm.lyrTree      ^= true;
			scope.vm.settings.sidebar_btn.form ^= true;
			scope.vm.settings.sidebar_btn.tbl_content ^= true;

			var searchIcon = angular.element( document.querySelector( '#searchIcon' ) ),
				editIcon   = angular.element( document.querySelector( '#editIcon' ) );

			if (scope.vm.insertInputs) {
				searchIcon.css('background-color', 'white');
				editIcon.css('background-color', '#2C709F');
			} else {
				searchIcon.css('background-color', '#2C709F');
				editIcon.css('background-color', 'white');
			}
		};
		
		scope.$watch('vm.sidebar.sidebar', LeafletControls.updateSidebarBtn(scope), true);

		///////////////////////////   End Section   ////////////////////////////

		// Leaflet map initialization
		scope.vm.map = L.map(mapElm, {
			minZoom     : scope.vm.settings.zoom.min,
			maxZoom     : scope.vm.settings.zoom.max,
			zoomControl : false,
			scale       : scope.vm.settings.scale
		});

		// Give position to things
		LeafletControls.positionElements(scope);

		// Add Scale to the Map
		LeafletControls.addScale(scope);

		// Set Maximum bounds
		LeafletControls.maxBounds(scope);

		/////////////////////////   Basemaps Control   /////////////////////////

		// Add basemap to the map
		// Default basemap
		scope.vm.basemap = "MAPBOX_STREETS";

		// Basemaps tree
		scope.vm.basemaps = BASEMAPS_TREE;

		// Change checked basemap
		scope.vm.changeBasemap = LeafletLayers.getBasemapName(scope);

		scope.$watch(
			'vm.basemap', LeafletLayers.changeBasemap(scope), true
		);

		///////////////////////////   End Section   ////////////////////////////

		//////////////////////////   Zoom Control   ///////////////////////////

		// Change view center
		scope.vm.settings.currentCenter = {
			lat: scope.vm.settings.center.lat,
			lng: scope.vm.settings.center.lng,
			zoom: scope.vm.settings.center.zoom
		};

		scope.$watch(
			'vm.settings.currentCenter',
			LeafletControls.changeMapCenter(scope), true
		);

		// Zoom to full extent
		scope.vm.zoomToFullExtent = LeafletControls.zoomToFullExtent(scope);

		// Zooom by boundary
		scope.vm.zoom_in  = false;
		scope.vm.zoom_out = false;
		scope.vm.drawZoom = false;
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
				zoomInElem = angular.element( document.querySelector( '#zoom-in' ) ),
				zoomOutElem = angular.element ( document.querySelector ( '#zoom-out') );

			if (currentZoomIn && !currentZoomOut) {
				zoomInElem.css('background-color', '#06b4d1');
				zoomOutElem.css('background-color', '#2C709F');
			} else if (!currentZoomIn && currentZoomOut) {
				zoomInElem.css('background-color', '#2C709F');
				zoomOutElem.css('background-color', '#06b4d1');
			} else if (!currentZoomIn && !currentZoomOut) {
				zoomInElem.css('background-color', '#2C709F');
				zoomOutElem.css('background-color', '#2C709F');
			} else {
				return;
			}
		};

		///////////////////////////   End Section   ////////////////////////////

		/////////////////////////  Overlays Control   //////////////////////////

		// Deal with the overlays
		// Create object to save all layers added to the map
		scope.vm.rqstLyr = undefined;
		
		// Get Layers List and add layers to the map
		scope.$watch('vm.rqstid', LeafletLayers.getLyrOnRqst(scope), true);

		// Create the overlays tree on the sidebar
		scope.$watch('vm.lyrParam', LeafletLayers.getOverlaysTree(scope), true);

		// Remove or Add Layer by click
		scope.vm.layerControl = LeafletLayers.layersControl(scope);
		scope.vm.geoserverLayerControl = LeafletLayers.geoserverLyrControl(scope);

		// Tree nodes open/close
		scope.vm.lyr_open = {'open': true, 'css': 'href_active'};
		scope.vm.base_open = {'open': true, 'css': 'href_active'};
		scope.vm.gsrv_open = {'open': true, 'css': 'href_active'};
		
		// Regular
		scope.vm.toogleNode = function(node) {
			node.open ^= true;
		};
		
		scope.vm.activeRef = function(node) {
			node.css = node.css === 'href_active' ? '' : 'href_active';
		};
		
		// Geoserver Tree
        scope.vm.toogleNodes = function(node) {
            node.fields.status ^= true;
        };

        scope.vm.activeRefs = function(node) {
            node.fields.css = node.fields.css === 'href_active' ? '' : 'href_active';
        };

		///////////////////////////   End Section   ////////////////////////////

		//////////////////////////   Draw Section   ///////////////////////////
		
		if (scope.vm.settings.draw.func === 'circulus') {
			var drawFunction = LeafletDraw.drawCircle;
			scope.vm.drawSomething = LeafletDraw.circleEvent(scope);
		} else if (scope.vm.settings.draw.func === 'rectangulus') {
			var drawFunction = LeafletDraw.drawRectangle;
			scope.vm.drawSomething = LeafletDraw.rectangleEvent(scope);
		} else {
			var drawFunction = undefined;
			scope.vm.drawSomething = undefined;
		}

		scope.$watch(
			'vm.settings.draw.edit',
			drawFunction(scope), true
		);

		// Deal with drawed objects
		scope.vm.drawnItems = L.featureGroup().addTo(scope.vm.map);

		scope.vm.map.on(L.Draw.Event.CREATED, scope.vm.drawSomething);

		// Del drawed layer
		// TODO: Function to delete other things
		scope.$watch('vm.settings.draw.delet', DelDrawedCircle(), true);

		function DelDrawedCircle() {
			return delDrawedCircle;

			function delDrawedCircle () {
				if (!scope.vm.settings.draw.delet) return;

				if (scope.vm.draw_lyr) {
					scope.vm.drawnItems.removeLayer(scope.vm.draw_lyr);
				}
				
				scope.vm.settings.draw.output = 'default';
				scope.vm.settings.draw.radius = undefined;
				scope.vm.settings.draw.delet  = false;
			}
		}

		///////////////////////////   End Section   ////////////////////////////
		
		scope.vm.popuphtml = '';
		
		scope.vm.closePopup = function() {
			scope.vm.popuphtml = '';
		};
		
		scope.vm.loading = false;
	}
}

LeafletMappingController.$inject = ['$scope'];

function LeafletMappingController($scope) {
	/* jshint validthis: true */
	var vm = this;
}

})();