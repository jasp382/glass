(function () {"use strict";

angular
	.module('jsidejs.directives')
	.directive('statUnitsManage', statUnitsManage);

statUnitsManage.$inject = [
	// Map Related
	'L', 'LeafLayers', 'LeafletControls', 'LeafletDraw', 'BASEMAPS_TREE',
	'Settings',
	// API Tools
	'$q',
	// API Endpoints
	'GrpStatsTable', 'GetDataset'];

function statUnitsManage(
	L, LeafLayers, LeafletControls, LeafletDraw, BASEMAPS_TREE,
	Settings,
	$q, GrpStatsTable, GetDataset) {
	var directive = {
		restrict         : 'E',
		replace          : false,
		transclude       : true,
		templateUrl      : '/static/stat-units-grp.html',
		scope : {
			wtodo  : '=',
			rqstid : '='
		},
		link             : link,
		controller       : statUnitsManageController,
		controllerAs     : 'vm',
		bindToController : true
	};
	
	return directive;
	
	function link(scope, iElement, iAttrs) {
		// O que a pagina deve mostrar
		if (scope.vm.wtodo === 101) {
			scope.vm.initial    = false;
			scope.vm.addStatGeom = true;
		} else {
			scope.vm.initial    = true;
			scope.vm.addStatGeom = false;
		};
		
		/* List Countries */
		scope.vm.countriesLst = undefined;
		scope.vm.getCountries = true;
		
		scope.$watch('vm.getCountries', GetCountries(), true);
		
		function GetCountries() {
			return getCountries;
			
			function getCountries () {
				if (scope.addStatGeom) return;
				
				var rawCountries = GrpStatsTable.query(),
					settings = Settings.query();
				
				$q.all([
					rawCountries.$promise, settings.$promise
				]).then(function () {
					scope.vm.countriesLst = rawCountries;
					
					var host = settings[0].host,
    					port = settings[0].port,
    					prot = settings[0].protocol,
						work = settings[0].workspace;
					
					scope.vm.countriesLst.forEach(function (d) {
						d.scale.forEach(function (s) {
							s['status'] = false;
							s['lyr'] = L.tileLayer.wms(
								prot + '://' + host + ':' + port + '/geoserver/ows?', {
									layers: work + ':' + d.slug + '_' + s.desig,
									transparent : true,
									format : 'image/png'
									//styles : 'Default'
							});
						});
					});
				});
			};
		};
		
		/* Get Statistic Unit for Some Country */
		scope.vm.statsLst = undefined;
		scope.vm.scalesLyr = undefined;
		
		scope.vm.selectCountry = function (grp) {
			scope.vm.addForm = false;
			scope.vm.scalesLyr = grp.fid;
			//scope.vm.statsLst = grp.stats;
		};
		
		/* Show form to add new group */
		scope.vm.addForm = undefined;
		
		scope.vm.showAddForm = function () {
			scope.vm.statsLst = undefined;
			scope.vm.addForm = true;
		}
		
		/* Get Datasets List */
		scope.vm.get_dataset = true;
		
		scope.$watch('vm.get_dataset', DatasetList(), true);
		
		function DatasetList() {
			return getDtList;
			
			function getDtList () {
				var data = GetDataset.query({fid:scope.vm.rqstid});
				
				$q.all([data.$promise]).then(function() {
					scope.vm.dataset = data[0];
				});
			};
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
		
		// Default basemap
		scope.vm.basemap = "MAPBOX_STREETS";
		
		// Basemaps tree
		scope.vm.basemaps = BASEMAPS_TREE;
		
		// Change checked basemap
		scope.vm.changeBasemap = LeafLayers.getBasemapName(scope);
		
		scope.$watch(
			'vm.basemap', LeafLayers.changeBasemap(scope), true
		);
		
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
		
		// Manage layers
		scope.vm.actualLyr = undefined;
		
		scope.vm.addNewLyr = function (row) {
			if (row.status) {
				if (!scope.vm.actualLyr) {
					scope.vm.actualLyr = row.lyr;
				} else {
					scope.vm.map.removeLayer(scope.vm.actualLyr);
					scope.vm.actualLyr = row.lyr;
					
					scope.vm.countriesLst.forEach(function (d) {
						d.scale.forEach(function (s) {
							if (s.fid !== row.fid && s.status) {
								s['status'] = false;
							}
						});
					});
				}
			
				scope.vm.map.addLayer(scope.vm.actualLyr);
			} else {
				scope.vm.map.removeLayer(scope.vm.actualLyr);
				scope.vm.actualLyr = undefined;
			}
		}
	};
};

statUnitsManageController.$inject = ['$scope'];

function statUnitsManageController($scope) {
	/* jshint validthis: true */
	var vm = this;
};

})();