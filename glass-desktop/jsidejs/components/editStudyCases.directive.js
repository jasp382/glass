(function () {'use strict';

angular
	.module('jsidejs.components')
	.directive('editStudyCases', editStudyCases);

editStudyCases.$inject = [
	// Map Related
	'L', 'LeafLayers', 'LeafletControls', 'LeafletDraw', 'BASEMAPS_TREE',
	// API Tools
	'$q',
	// API Endpoints
	'GrpStatsTable'
];

function editStudyCases(
	L, LeafLayers, LeafletControls, LeafletDraw, BASEMAPS_TREE,
	$q, GrpStatsTable
) {
	var directive = {
		restrict        : 'E',
		replace         : false,
		transclude      : true,
		templateUrl     : '/static/partials/edit-study-cases.html',
		scope: {
			addcases : '=',
			editcase : '='
		},
		link            : link,
		controller      : editStudyCasesController,
		controllerAs    : 'vm',
		bindToController: true
	};
	
	return directive;
	
	function link(scope, iElement, iAttrs) {
		// Disable directive
		scope.vm.disableForm = function () {
			scope.vm.addcases = false;
			scope.vm.editcase = false;
		};
		/////////////////////////   Add Study Cases   ///////////////////////
		
		// Manage user options for adding study case areas
		scope.vm.how_to_a           = undefined;
		scope.vm.show_map_input     = undefined;
		scope.vm.show_coord_input_a = undefined;
		scope.vm.show_map_input_a   = undefined;
		scope.vm.show_file_input_a  = undefined;
		
		scope.vm.how_to_b           = undefined;
		scope.vm.show_coord_input_b = undefined;
		scope.vm.show_map_input_b   = undefined;
		scope.vm.show_file_input_b  = undefined;
		
		// When user select one option, show what is needed
		scope.$watch('vm.how_to_a', showGeoOptions, true);
		scope.$watch('vm.how_to_b', showGeoOptionsB, true);
		
		function showGeoOptions () {
			if (scope.vm.how_to_a === 'coord') {
				scope.vm.show_coord_input_a = true;
				scope.vm.show_map_input_a   = false;
				scope.vm.show_file_input_a  = false;
			} else if (scope.vm.how_to_a === 'mapa') {
				scope.vm.show_coord_input_a = false;
				scope.vm.show_map_input_a   = true;
				scope.vm.show_file_input_a  = false;
			} else if (scope.vm.how_to_a === 'upfile') {
				scope.vm.show_coord_input_a = false;
				scope.vm.show_map_input_a   = false;
				scope.vm.show_file_input_a  = true;
			} else {
				scope.vm.show_coord_input_a = false;
				scope.vm.show_map_input_a   = false;
				scope.vm.show_file_input_a  = false;
			}
		};
		
		function showGeoOptionsB () {
			if (scope.vm.how_to_b === 'coord') {
				scope.vm.show_coord_input_b = true;
				scope.vm.show_map_input_b   = false;
				scope.vm.show_file_input_b  = false;
			} else if (scope.vm.how_to_b === 'mapa') {
				scope.vm.show_coord_input_b = false;
				scope.vm.show_map_input_b = true;
				scope.vm.show_file_input_b  = false;
			} else if (scope.vm.how_to_b === 'upfile') {
				scope.vm.show_coord_input_b = false;
				scope.vm.show_map_input_b   = false;
				scope.vm.show_file_input_b  = true;
			} else {
				scope.vm.show_coord_input_b = false;
				scope.vm.show_map_input_b   = false;
				scope.vm.show_file_input_b  = false;
			}
		};
		
		// Edit Study cases
		scope.vm.newname = (' ' + scope.vm.editcase.slug).slice(1);
		scope.vm.newDesc = (' ' + scope.vm.editcase.descricao).slice(1);
		
		// Groups of Statistic Units
		scope.vm.StatsGrpOptions = true;
		
		scope.$watch('vm.StatsGrpOptions', getStatUnitsGrp, true);
		
		function getStatUnitsGrp () {
			var rawGrp = GrpStatsTable.query({fields : 'fid,descricao'});
			
			$q.all([rawGrp.$promise]).then(function () {
				scope.vm.StatsGrpOptions = rawGrp;
			});
		};
		
		/////////////////////////   Map Initialization   ///////////////////////
		scope.vm.settings = {
        	center: {
            	lat: 39.6818,
            	lng: -7.96643,
            	zoom: 7
        	},
        	scale: true,
        	zoom: {
            	min: 7,
            	max: 20
        	},
        	click: {
            	show: false,
            	output: ''
        	},
        	bounds: {
            	top: 42.154311,
            	right: -6.189159,
            	bottom: 36.961710,
            	left: -9.500527
        	},
        	position: {
            	scale: 'bottomright'
        	}
    	};
		var mapElm = iElement[0].firstChild;
		scope.vm.map = L.map(mapElm, {
			minZoom : scope.vm.settings.zoom.min,
			maxZoom : scope.vm.settings.zoom.max,
			zoomControl : false,
			scale : scope.vm.settings.scale
		});
		
		// Give position to things
		LeafletControls.positionElements(scope);
		
		// Add Scale to the Map
		LeafletControls.addScale(scope);
		
		// Set Maximum bounds
		LeafletControls.maxBounds(scope);
		
		/////////////////////////   Basemaps Control   /////////////////////////
		
		// Default basemap
		scope.vm.basemap = "MAPBOX_STREETS";
		
		// Basemaps tree
		scope.vm.basemaps = BASEMAPS_TREE;
		
		// Change checked basemap
		scope.vm.changeBasemap = LeafLayers.getBasemapName(scope);
		
		scope.$watch(
			'vm.basemap', LeafLayers.changeBasemap(scope), true
		);
		
		//////////////////////////   Zoom Control   ///////////////////////////
		
		// Change view center
		scope.vm.settings.currentCenter = {
			lat  : scope.vm.settings.center.lat,
			lng  : scope.vm.settings.center.lng,
			zoom : scope.vm.settings.center.zoom
		};
		
		scope.$watch(
			'vm.settings.currentCenter',
			LeafletControls.changeMapCenter(scope), true
		);
		
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
		scope.vm.drawEdit = false;
		scope.vm.drawWhat = false;
		var drawFunction = LeafletDraw.drawRectangle;
		scope.vm.drawSomething = LeafletDraw.rectangleEvent(scope);
		
		scope.vm.top_coord      = undefined;
		scope.vm.bottom_coord   = undefined;
		scope.vm.left_coord     = undefined;
		scope.vm.right_coord    = undefined;
		scope.vm.top_coord_b    = undefined;
		scope.vm.bottom_coord_b = undefined;
		scope.vm.left_coord_b   = undefined;
		scope.vm.right_coord_b  = undefined;
		
		scope.$watch('vm.drawEdit', drawFunction(scope), true);
			
		scope.vm.enableDraw = function (what_to_do) {
			scope.vm.drawEdit = true;
			scope.vm.drawWhat = what_to_do;
		};
		
		// Deal with drawed objects
		scope.vm.drawnItems = L.featureGroup().addTo(scope.vm.map);
		
		scope.vm.map.on(L.Draw.Event.CREATED, scope.vm.drawSomething);
	};
};

editStudyCasesController.$inject = ['$scope'];

function editStudyCasesController($scope) {
	/* jshint validthis: true */
	var vm = this;
};

})();