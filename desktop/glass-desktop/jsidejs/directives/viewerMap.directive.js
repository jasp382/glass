(function () {"use strict";

angular
	.module('jsidejs.directives')
	.directive('viewerMapping', viewerMapping);

viewerMapping.$inject = [
	'L', '$window', '$http', 'LeafLayers', 'LeafletControls', 'BASEMAPS_TREE'
];

function viewerMapping(L, $window, $http, LeafLayers, LeafletControls, BASEMAPS_TREE) {
	var directive = {
		restrict         : 'E',
		replace          : false,
		transclude       : true,
		templateUrl      : '/static/viewer-maps.html',
		scope : {
			caseid  : '=',
			ctop    : '=',
			cbottom : '=',
			cleft   : '=',
			cright  : '=',
			ctxtop  : '=',
			ctxbot  : '=',
			ctxlef  : '=',
			ctxrig  : '='
		},
		link             : link,
		controller       : viewerMappingController,
		controllerAs     : 'vm',
		bindToController : true
	};
	
	return directive;
	
	function link(scope, iElement, iAttrs) {
		// Get id for the map
		var mapElm    = iElement[0].children[1],
			mapElmCtx = iElement[0].children[0];
		
		// initial css class for the map
		//angular.element(mapElm).addClass('map-with-sidebar');
		
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
			extent_ctx : L.latLngBounds(
				L.latLng(scope.vm.ctxtop, scope.vm.ctxlef),
				L.latLng(scope.vm.ctxbot, scope.vm.ctxrig)
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
		
		// Main Map
		scope.vm.map = L.map(mapElm, {
			minZoom     : scope.vm.settings.zoom.min,
			maxZoom     : scope.vm.settings.zoom.max,
			zoomControl : false,
			scale       : scope.vm.settings.scale
		});
		
		// Lateral Map
		scope.vm.map_ctx = L.map(mapElmCtx, {
			minZoom     : scope.vm.settings.zoom.min,
			maxZoom     : scope.vm.settings.zoom.max,
			zoomControl : false,
			scale       : scope.vm.settings.scale
		});
		
		scope.vm.map.fitBounds(scope.vm.settings.extent);
		scope.vm.map_ctx.fitBounds(scope.vm.settings.extent_ctx);
		
		scope.vm.settings.center.lat = scope.vm.map.getCenter().lat;
		scope.vm.settings.center.lng = scope.vm.map.getCenter().lng;
		scope.vm.settings.center.zoom = scope.vm.map.getZoom();
		
		// Give position to things
		LeafletControls.positionElements(scope);
		
		// Add Scale to the Map
		LeafletControls.addScale(scope);
		
		// Set Maximum bounds
		LeafletControls.maxBounds(scope);
		
		/////////////////////////   Basemaps Control   /////////////////////////
		
		// Default basemap
		scope.vm.basemap     = "MAPBOX_STREETS";
		scope.vm.basemap_ctx = "MAPBOX_STREETS";
		
		// Basemaps tree
		scope.vm.basemaps = BASEMAPS_TREE;
		
		// Change checked basemap
		scope.vm.changeBasemap = LeafLayers.getBasemapName(scope);
		
		scope.$watch(
			'vm.basemap', LeafLayers.changeBasemap(scope), true
		);
		
		scope.$watch(
			'vm.basemap_ctx', LeafLayers.SetCtxBasemap(scope), true
		);
		
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
		
		scope.vm.drawnItems = L.featureGroup().addTo(scope.vm.map);
		
		scope.vm.map.on(L.Draw.Event.CREATED, function(event) {
			LeafletControls.executeZoom(scope, event);
		});
		
		//////////////////////////  Overlay Control  ///////////////////////////
		scope.vm.getLayers = true;
		scope.vm.lyr_geoserver = {};
		scope.vm.tbl_contents = [];
		scope.vm.lyr_active = undefined;
		
		scope.vm.lyr_year = undefined;
		scope.vm.new_lyr = undefined;
		
		// Remove or Add Layer by click
		scope.vm.ctxLyrControl = LeafLayers.contextLyrControl(scope);
		
		//scope.$watch('vm.getLayers', LeafLayers.getCtxLyr(scope), true);
		scope.$watch('vm.getLayers', LeafLayers.getLayersByYear(scope), true);
		
		scope.$watch('vm.lyr_year', changeLyrLst, true);
		scope.$watch('vm.new_lyr', addNewLyr, true);
		
		function changeLyrLst () {
			if (!scope.vm.lyr_year) return;
			
			scope.vm.new_lyr = undefined;
			scope.vm.lst_lyr = scope.vm.av_lyr[scope.vm.lyr_year];
		};

		// Add Base Layers to map
		scope.$watch('vm.getLayers', LeafLayers.GetBaseLayers(scope), true);
		
		function addNewLyr() {
			if (!scope.vm.new_lyr) return;
			
			// TODO: check if layer was already added
			
			var lyr = scope.vm.lst_lyr[Number(scope.vm.new_lyr)];
			
			lyr['layer'] = L.tileLayer.wms(lyr.url, {
				layers : lyr.lname,
				transparent : true,
				format : 'image/png',
				styles : lyr.style
			});
			
			lyr['dlayer'] = L.tileLayer.wms(lyr.url, {
				layers : lyr.dname,
				transparent: true,
				format : 'image/png',
				styles : lyr.style
			});
			
			scope.vm.tbl_contents.unshift(lyr);

			/* Order Layer Legend by */
			lyr.lyr_cls.sort(function (a, b) {
				return a-b;
			});
			
			scope.vm.map.addLayer(lyr.dlayer);
			scope.vm.map_ctx.addLayer(lyr.layer);

			scope.vm.polyLyr.forEach(function (l) {
				if (l.status) {
					scope.vm.map.removeLayer(l.lyr);
					scope.vm.map.addLayer(l.lyr);
				}
			});
		};
		
		scope.vm.activeLyrControl = function (lyr, idx) {
			if (lyr.status) {
				var __idx = Number(idx);
				
				scope.vm.map.addLayer(lyr.dlayer);
				scope.vm.map_ctx.addLayer(lyr.layer);
				
				if (idx > 0) {
					for (var i=idx-1; i>= 0 && i < idx; i--) {
						if (scope.vm.tbl_contents[i].status) {
							scope.vm.map.removeLayer(
								scope.vm.tbl_contents[i].dlayer);
							scope.vm.map_ctx.removeLayer(
								scope.vm.tbl_contents[i].layer);
							scope.vm.map.addLayer(
								scope.vm.tbl_contents[i].dlayer);
							scope.vm.map_ctx.addLayer(
								scope.vm.tbl_contents[i].layer
							);
						}
					}
				}

				scope.vm.polyLyr.forEach(function (l) {
					if (l.status) {
						scope.vm.map.removeLayer(l.lyr);
						scope.vm.map.addLayer(l.lyr);
					}
				});
				
				lyr.status = true;
			} else {
				scope.vm.map.removeLayer(lyr.dlayer);
				scope.vm.map_ctx.removeLayer(lyr.layer);
				
				lyr.status = false;
			}
		};

		scope.vm.pntLyrControl = function (lyr, idx) {
			if (lyr.status) {
				scope.vm.map.addLayer(lyr.lyr);

				lyr.status = true;
			} else {
				scope.vm.map.removeLayer(lyr.lyr);
				lyr.status = false;
			}
		}; 
		
		// Get Feature Info
		scope.vm.map.on('click', function (event) {
			var clickPnt = scope.vm.map.latLngToContainerPoint(
				event.latlng, scope.vm.map.getZoom()),
				size = scope.vm.map.getSize(),
				_url = '/api/gsrv/featinfo/wengine/det_' + 
					scope.vm.tbl_contents[0].fid + '/?' +
					'WIDTH=' + String(size.x) + '&HEIGHT=' + String(size.y) +
					'&X=' + String(clickPnt.x) + '&Y=' + String(clickPnt.y) +
					'&BBOX=' + String(scope.vm.map.getBounds().toBBoxString());
			
			$http({
				method: 'GET',
				url   : _url
			}).then(function (response) {
				var popup = L.popup(),
					feat  = response.data.features[0];
				
				if (!feat) return;
				
				popup
					.setLatLng(event.latlng)
					.setContent(
						"<p><b>" + feat.properties.tipo + ": </b>" +
						String(feat.properties.design) + "</p>" +
						"<p><b>Tema: </b>" + String(feat.properties.lname) + "</p>" +
						"<p><b>Ano: </b>" + String(feat.properties.year) + "</p>" +
						"<p><b>Valor: </b>" + String(feat.properties.value) + "</p>" +
						"<p><b>Unidade: </b>" + String(feat.properties.lunit) + "</p>"
					).openOn(scope.vm.map);
			});
		});
		
		scope.vm.map_ctx.on('click', function (event) {
			var clickPnt = scope.vm.map_ctx.latLngToContainerPoint(
				event.latlng, scope.vm.map_ctx.getZoom()),
				size = scope.vm.map_ctx.getSize(),
				_url = '/api/gsrv/featinfo/wengine/lyr_' + 
					scope.vm.tbl_contents[0].fid + '/?' +
					'WIDTH=' + String(size.x) + '&HEIGHT=' + String(size.y) +
					'&X=' + String(clickPnt.x) + '&Y=' + String(clickPnt.y) +
					'&BBOX=' + String(scope.vm.map_ctx.getBounds().toBBoxString());
			
			$http({method : 'GET', url : _url}).then(function (response) {
				var feat  = response.data.features[0];
				
				if (!feat) return;
				
				scope.vm.ctxClickValue = feat.properties.value;
				scope.vm.ctxClickColor = feat.properties.color;
				scope.vm.ctxClickDesi  = feat.properties.design;
			});
		});
		
		////////////////////////  Data Table Control  ////////////////////////
		scope.$watch('vm.new_lyr', GetTable(), true);
		scope.vm.lyrTbl = undefined;
		scope.vm.lyrObj = undefined;
		
		function GetTable() {
			return getTable;
			
			function getTable () {
				if (!scope.vm.new_lyr) return;
				
				scope.vm.lyrObj = scope.vm.lst_lyr[Number(scope.vm.new_lyr)];
				var _url = '/api/dbviews/det_' + scope.vm.lyrObj.fid + 
					'/?fields=fid,asu_fid,value,design,lname,year,cls,color';
				
				$http({method: 'GET', url: _url}).then(function (response) {
					scope.vm.lyrTbl = response.data;
				});
			}
		}
	};
};

viewerMappingController.$inject = ['$scope'];

function viewerMappingController($scope) {
	/* jshint validthis: true */
	var vm = this;
}

})();