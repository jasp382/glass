(function () {'use strict';

angular
	.module('jsidejs.services')
	.service('LeafLayers', LeafLayers);

LeafLayers.$inject = [
	'BASEMAP_OPTIONS', 'L', 'MAPBOX_KEY', 'MAPBOX_STREETS_ATTRIBUTION',
	'MAPBOX_STREETS_ID', 'GOOGLE_EARTH', 'GOOGLE_MAPS',
	'OSM_URL', 'OSM_ATTRIBUTION', '$q', 'Indicators', 'Settings',
	'LayersTbl', 'YearsLyrTbl', 'PntLyrTbl', 'PolyLyrTbl', '$http'
];


function LeafLayers(
		BASEMAP_OPTIONS, L, MAPBOX_KEY, MAPBOX_STREETS_ATTRIBUTION,
		MAPBOX_STREETS_ID, GOOGLE_EARTH, GOOGLE_MAPS,
		OSM_URL, OSM_ATTRIBUTION, $q, IndicatorsTable, Settings,
		LayersTbl, YearsLyrTbl, PntLyrTbl, PolyLyrTbl, $http) {
	/* Functions to Control Leaflet Maps */
	
	var service = {
		changeBasemap         : SetBasemap,
		getBasemapName        : GetBasemap,
		contextLyrControl     : ContextLyrControl,
		getIndicatorTreeArray : GetIndicatorsTree,
		getLayersByYear       : GetLyrByYear,
		SetCtxBasemap         : SetCtxBasemap,
		GetBaseLayers         : GetBaseLyr,
		setBasemapOnMap       : setBasemapOnMap,
		obtainLyrByYear       : obtainLyrByYear
	};
	
	return service;
	
	/////////////////////////////
	
	// Get Basemap SLUG by name
    function GetBasemap(scope) {
        return getBasemap;
        
        function getBasemap(cls, bm) {
            if (scope.vm.basemaps[cls][1][bm]) return;
        
            scope.vm.basemap = BASEMAP_OPTIONS[bm];
        
            scope.vm.basemaps[cls][1][bm] = true;
        
            for (var _cls in scope.vm.basemaps) {
                for (var b in scope.vm.basemaps[_cls][1]) {
                    if (b !== bm && scope.vm.basemaps[_cls][1][b]) {
                        scope.vm.basemaps[_cls][1][b] = false;
                    }
                }
            }
        };
    };
	
	// Set & Change Basemap
	function SetBasemap(scope) {
		return setBasemap;
		
		function setBasemap() {
			if (scope.vm.basemap_layer) {
				scope.vm.map.removeLayer(scope.vm.basemap_layer);
			}
		
			if (scope.vm.basemap === 'MAPBOX_STREETS') {
				scope.vm.basemap_layer = L.tileLayer(MAPBOX_KEY, {
					maxZoom: scope.vm.settings.zoom.max,
					attribution: MAPBOX_STREETS_ATTRIBUTION,
					id: MAPBOX_STREETS_ID
				});
			} else if (scope.vm.basemap === 'GOOGLE_EARTH') {
				scope.vm.basemap_layer = L.tileLayer(GOOGLE_EARTH, {
					attribution: '&copy; Google Earth'
				});
			} else if (scope.vm.basemap === 'GOOGLE_MAPS') {
				scope.vm.basemap_layer = L.tileLayer(GOOGLE_MAPS, {
					maxZoom: scope.vm.settings.zoom.max,
					subdomain: '0123',
					attribution: '&copy; Google Maps'
				});
			} else if (scope.vm.basemap === 'OSM') {
				scope.vm.basemap_layer = L.tileLayer(OSM_URL, {
					maxZoom: scope.vm.settings.zoom.max,
					attribution: OSM_ATTRIBUTION
				});
			} else {
				scope.vm.basemap_layer = L.esri.basemapLayer(scope.vm.basemap);
			}
		
			scope.vm.map.addLayer(scope.vm.basemap_layer);
		}
	};
	
	function SetCtxBasemap(scope) {
		return setCtxBasemap;
		
		function setCtxBasemap() {
			scope.vm.bmlyr = L.tileLayer(MAPBOX_KEY, {
				maxZoom: scope.vm.settings.zoom.max,
				attribution: MAPBOX_STREETS_ATTRIBUTION,
				id: MAPBOX_STREETS_ID
			});
			
			scope.vm.map_ctx.addLayer(scope.vm.bmlyr);
		}
	}
    
    // Functions to help in the creation of Layers Tree
    function GetIndicatorsTree(scope) {
    	return getIndicatorsTree();
    	
    	function getIndicatorsTree() {
    		var rawIndicators = IndicatorsTable.query(),
    			settings      = Settings.query();
    		
    		$q.all([
    			rawIndicators.$promise,
    			settings.$promise
    		]).then(function () {
    			// Get Roots
    			scope.vm.layerTree = getRootNodes(rawIndicators);
    			// Assign childs to roots
    			getChildNodes(scope.vm.layerTree, rawIndicators);
    			// Create Leaflet Layers Objects
    			CreateLayers(scope.vm.layerTree, settings);
    		});
    	};
    	
    	function getRootNodes(data) {
    		var nodes_array = [];
    		
    		data.forEach(function (d) {
    			if (d.fields.child_of === 0) {
    				d.fields['status'] = false;
    				d.fields['css']    = 'href_active';
    				nodes_array.push(d);
    			}
    		});
    		
    		return nodes_array;
    	};
    	
    	function getChildNodes(rootNodes, data) {
    		rootNodes.forEach(function (d) {
    			data.forEach(function (e) {
    				if (d.pk === e.fields.child_of) {
    					e.fields['status'] = false;
    					e.fields['css'] = 'href_active';
    					
    					// Is layer?
    					if (e.fields.islyr === 1) {
    						if (!d.fields.layers) {
    							d.fields['layers'] = [e];
    						} else {
    							d.fields.layers.push(e);
    						}
    					} else {
    						// is not a layer
    						if (!d.fields.child) {
    							d.fields['child'] = [e];
    						} else {
    							d.fields.child.push(e);
    						}
    					}
    				}
    			});
    			
    			// Do it for all existent sub-children
    			if (!!d.fields.child) {
    				getChildNodes(d.fields.child, data);
    			};
    		});
    	};
    	
    	function CreateLayers(nodes, set) {
			nodes.forEach(function (theme) {
				if (theme.fields.layers) {
					createLayers(theme.fields.layers, set);
				}
				
				if (theme.fields.child) {
					CreateLayers(theme.fields.child, set);
				}
			});
		};
		
		function createLayers(layers, SETTINGS) {
			if (!layers) return;
			
			var host = SETTINGS[0].GEOSERVER.HOST,
				port = SETTINGS[0].GEOSERVER.PORT,
				prot = SETTINGS[0].GEOSERVER.PROTOCOL;
			
			layers.forEach(function (d) {
				var wmsLayer = L.tileLayer.wms(
					prot + '://' + host + ':' + port + '/geoserver/ows?', {
						layers : 'justside:atlas_municipios',
						transparent : true,
						format : 'image/png',
						styles: 'atlas_municipios_' + d.fields.slug + '_2011'
				});
				
				scope.vm.lyr_geoserver[d.fields.slug] = wmsLayer;
			});
		};
    };

	// Remove or Add Layer by click - Context Layers
    function ContextLyrControl (scope) {
    	return contextLyrControl;
    	
    	function contextLyrControl (lyr) {
    		if (lyr.status) {
    			scope.vm.map_ctx.addLayer(lyr.layer);

				scope.vm.ctxTree.forEach(function (l) {
					if(l.fid !== lyr.fid && l.status) {
						scope.vm.map_ctx.removeLayer(l.layer);
						
						l.status = false;
					}
				});
    		} else {
    			scope.vm.map_ctx.removeLayer(lyr.layer);
    		};
    	}
    };
    
	/////////////////////////////
	
	function GetLyrByYear(scope) {
		return getLyrByYear();
		
		function getLyrByYear() {
			var rawYears = YearsLyrTbl.query({
				case:scope.vm.caseid}),
				settings = Settings.query();
			
			scope.vm.av_lyr = {};
			
			$q.all([
				rawYears.$promise,
				settings.$promise
			]).then(function () {
				var host = settings[0].host,
					port = settings[0].port,
					prot = settings[0].protocol,
					work = settings[0].workspace;
				
				rawYears.forEach(function (y) {
					var rawLyr = LayersTbl.query({
						case:scope.vm.caseid,
						year: y.fid
					});
					
					var url = prot + '://' + host + ':' + port + '/geoserver/ows?';
					
					scope.vm.av_lyr[y.year] = [];
					
					$q.all([
						rawLyr.$promise
					]).then(function () {
						rawLyr.forEach(function (l) {
							l['name'] = l.id_indicator.name;
							l['url'] = url;
							l['lname'] = work + ':lyr_' + l.fid;
							l['dname'] = work + ':det_' + l.fid;
							l['status'] = true;
							
							scope.vm.av_lyr[y.year].push(l);
						})
					});
				});
			})
		}
	};

	function obtainLyrByYear(lyrsObj, caseid) {
		return getLyrByYear();
		
		function getLyrByYear() {
			var rawYears = YearsLyrTbl.query({
				case:caseid}),
				settings = Settings.query();
			
			$q.all([
				rawYears.$promise,
				settings.$promise
			]).then(function () {
				var host = settings[0].host,
					port = settings[0].port,
					prot = settings[0].protocol,
					work = settings[0].workspace;
				
				rawYears.forEach(function (y) {
					var rawLyr = LayersTbl.query({
						case:caseid,
						year: y.fid
					});
					
					var url = prot + '://' + host + ':' + port + '/geoserver/ows?';
					
					lyrsObj[y.year] = [];
					
					$q.all([
						rawLyr.$promise
					]).then(function () {
						rawLyr.forEach(function (l) {
							l['name'] = l.id_indicator.name;
							l['url'] = url;
							l['lname'] = work + ':lyr_' + l.fid;
							l['dname'] = work + ':det_' + l.fid;
							l['status'] = true;
							
							lyrsObj[y.year].push(l);
						})
					});
				});
			})
		}
	};

	function GetBaseLyr(scope) {
		return getBaseLyr;

		function getBaseLyr () {
			var rawPntLyr = PntLyrTbl.query({
					case : scope.vm.caseid}),
				rawPolyLyr = PolyLyrTbl.query({
					case: scope.vm.caseid
				}),
				settings = Settings.query();

			$q.all([
				rawPntLyr.$promise, rawPolyLyr.$promise, settings.$promise
			]).then(function () {
				scope.vm.pntLyr = rawPntLyr;
				scope.vm.polyLyr = rawPolyLyr;

				var host = settings[0].host,
					port = settings[0].port,
					prot = settings[0].protocol,
					work = settings[0].workspace;

				scope.vm.pntLyr.forEach(function (l) {
					l['url'] = '/api/gsrv/wfs/pnt_' + l.fid + '/';
					
					$http({
						method : 'GET',
						url    : l.url
					}).then(function (response) {
						var jresp = response.data;

						l['lyr'] = L.geoJson(jresp, {
							pointToLayer : function (feature, latlng) {
								var f_icon = L.icon({
									iconUrl: l.icon,
									iconSize : [25, 30],
									iconAnchor : [12.5, 30],
									popupAnchor : [0, -30]
								});

								var __lyr = L.marker(latlng, {icon : f_icon});

								__lyr.bindPopup(getPopupStrPnt(
									feature, l.name
								));

								return __lyr;
							}
						});

						scope.vm.map.addLayer(l.lyr);
						l['status'] = true;
					});
				});

				scope.vm.polyLyr.forEach(function (l) {
					l['url'] = prot + '://' + host + ':' + port + '/geoserver/ows?'
					l['status'] = true;

					l['lyr'] = L.tileLayer.wms(l.url, {
						layers : 'poly_' + l.fid,
						transparent : true,
						format : 'image/png',
						styles : 'red_stroke'
					});

					scope.vm.map.addLayer(l.lyr);
				});
			});
		}
	};

	function getPopupStrPnt(feat, title) {
		var str_popup = "<b>" + title + '</b><br>';

		for (var field in feat.properties) {
			if (feat.properties.hasOwnProperty(field)) {
				str_popup += "<b>" + field + ": </b>" + feat.properties[field]
					+ '<br>';
			}
		}

		return str_popup;
	};

	////////////////////////////////
	/**
	 * Add basemap and return layer
	 */

	function setBasemapOnMap(mapObj, lyr, maxZoom) {
		return setBasemap;

		function setBasemap() {
			lyr = L.tileLayer(MAPBOX_KEY, {
				maxZoom: maxZoom,
				attribution: MAPBOX_STREETS_ATTRIBUTION,
				id: MAPBOX_STREETS_ID
			});

			mapObj.addLayer(lyr);
		}
	};
};

})();