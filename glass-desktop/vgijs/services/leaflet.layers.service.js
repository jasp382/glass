(function () {'use strict';

angular
    .module('vgijs.services')
    .service('LeafletLayers', LeafletLayers);

LeafletLayers.$inject = [
    'BASEMAP_OPTIONS',
    'L',
    'MAPBOX_KEY',
    'MAPBOX_STREETS_ATTRIBUTION',
    'MAPBOX_STREETS_ID',
    'GOOGLE_EARTH',
    'GOOGLE_MAPS',
    'OSM_URL',
    'OSM_ATTRIBUTION',
    '$http',
    'LeafletThematicLayers',
    '$routeParams',
    '$q',
    'ViewLayers', 'ListLyrOsmToLulc', 'ListLyrDsn',
    'Settings', 'API_URL'
];

function LeafletLayers(BASEMAP_OPTIONS,
                      L,
                      MAPBOX_KEY,
                      MAPBOX_STREETS_ATTRIBUTION,
                      MAPBOX_STREETS_ID,
                      GOOGLE_EARTH,
                      GOOGLE_MAPS,
                      OSM_URL,
                      OSM_ATTRIBUTION,
                      $http,
                      LeafletThematicLayers,
                      $routeParams,
                      $q,
                      ViewLayers, ListLyrOsmToLulc, ListLyrDsn,
                      Settings, API_URL
) {
    var service = {
        getLyrRqstId        : getLayersRequest,
        addLyrUsingUrl      : AddGeoDataFromUrl,
        changeBasemap       : SetBasemap,
        getBasemapName      : GetBasemap,
        getLayerProperties  : GetLayersProperties,
        getOverlaysTree     : GetOverlaysTree,
        layersControl       : LayersControl,
        geoserverLyrControl : GeoserverLyrControl,
        addLyrFromGeoServer : GetOverlaysByTheme,
		listLyrByRqst       : listLyrByRqst,
		getLyrOnRqst        : GetLyrOnRqst
    };
    
    return service;
    
    /////////////////////////////
	function GetLyrOnRqst(scope) {
		return getLyrOnRqst;
		
		function getLyrOnRqst () {
			if (!scope.vm.rqstid) return;
			
			if (scope.vm.servname === 'osmtolulc') {
				var tblQ = ListLyrOsmToLulc.query({'fid' : scope.vm.rqstid});
			} else if (scope.vm.servname === 'dsn-search') {
				var tblQ = ListLyrDsn.query({'fid' : scope.vm.rqstid});
			} else {
				return;
			}
			
			$q.all([tblQ.$promise]).then(function () {
				scope.vm.rqstLyr = tblQ[0].lyr_rqsts;
				
				scope.vm.rqstLyr.forEach(function (l) {
					l['status'] = true;
					
					if (l.lyrt === 'geoserver') {
							
						l['lyr'] = L.tileLayer.wms(l.url, {
							layers : l.lname,
							transparent : true,
							format : 'image/png',
							styles : l.style
						});
							
						scope.vm.map.addLayer(l.lyr);
					} else {
						$http({method : 'GET', url : l.url}).then(function (r) {
							var jr = r.data;
							
							l['lyr'] = LeafletThematicLayers.getLayer(
								l.style, jr, scope, l.url
							);
							
							l.lyr.addTo(scope.vm.map);
							scope.vm.map.fitBounds(l.lyr.getBounds());
						});
					}
				});
			});
		}
	};
    
    function getLayersRequest(url) {
        /* Get the REQUEST_ID to be used to retrieve leaflet Layers
        parameters from the API. It is being parsed via URL */

        var get_params = url.split('?')[1];
        if (get_params === undefined) return undefined;
        var _get_params = get_params.split('&');
        var request_id;
        var field_name;
        _get_params.forEach(function(d) {
            var name_value = d.split('=');
            if (name_value[0] === 'layers_id') {
                request_id = Number(name_value[1]);
            } else { 
                request_id = request_id ? request_id : undefined;
            };

            if (name_value[0] === 'layers_field') {
                field_name = name_value[1];
            } else {
                field_name = field_name ? field_name : undefined;
            };
        });
        
        if (field_name && request_id) {
        	var lyrParam = {};
        	lyrParam[field_name] = request_id;
        } else {
        	var lyrParam = undefined;
        };

        return lyrParam;
    }

	function listLyrByRqst(mapVm, url) {
		/* Get Layers related with one request */
		
		return lstLyrByRqst;
		
		function lstLyrByRqst () {
			var rqstFID = url.searchParams.get('rqst');
		
			if (!rqstFID) return;
		
			$http({
				method : 'GET',
				url    : API_URL + '/api/rest/osmtolulc/rqsts/?fid=' + rqstFID
			}).then(function (response) {
				var jresp = response.data;
			
				mapVm.interactiveMapLayersID = jresp.lyr_rqsts;
			});
		}
	};
    
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
    
    
    // Change basemap
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
    }
    
    /////////////////////////////
    
    function AddGeoDataFromUrl(scope) {
        return addGeoDataFromUrl;
        
        function addGeoDataFromUrl() {
            var overlays = scope.vm.lyrParam;
            if (overlays === undefined) return;
            
            overlays.forEach(function(d) {
            	if (d.url.indexOf('geoserver') > -1) {
            		// Add layer from Geoserver
            		var settings = Settings.query();
            		
            		$q.all([
            			settings.$promise
            		]).then(function () {
            			var host     = settings[0].GEOSERVER.HOST;
            			var port     = settings[0].GEOSERVER.PORT;
            			var protocol = settings[0].GEOSERVER.PROTOCOL;
            			
            			var wmsLayer = L.tileLayer.wms(
            				protocol + '://' + host + ':' + port + '/geoserver/ows?', {
            					layers : d.url.split('|')[1],
            					transparent : true,
            					format: 'image/png',
            					styles: d.lyrtag
            			});
            			
            			scope.vm.map.addLayer(wmsLayer);
            			scope.vm.lyr_saved[d.name] = wmsLayer;
            		});
            	} else {
            		$http({
            			method: 'GET',
            			url: d.url
            		}).then(function (response) {
            			var json_response = response.data;
            			var lyr = LeafletThematicLayers.getLayer(
            				d.lyrtag, json_response, scope, d.url);
            			
            			lyr.addTo(scope.vm.map);
            			scope.vm.map.fitBounds(lyr.getBounds());
            			scope.vm.lyr_saved[d.name] = lyr;
            		});
            	}
            });
        }
    }

    /////////////////////////////
    // Get Layer Properties using one REQUEST_ID
    function GetLayersProperties(scope) {
        return getLayersProperties;

        function getLayersProperties() {
            if (!scope.vm.overlay) return;

            var layers = ViewLayers.query(scope.vm.overlay);

            $q.all([
                layers.$promise
            ]).then(function () {
            	scope.vm.lyrParam = [];
            	
            	layers.forEach(function(d) {
            		scope.vm.lyrParam.push({
            			name     : d.fields.name,
            			url      : d.fields.url,
            			lyrtag   : d.fields.style,
            			download : d.fields.download
            		});
            	});
            });
        }
    };
    
    // Generate layer tree using layers that came from URL
    function GetOverlaysTree(scope) {
        return getOverlaysTree;

        function getOverlaysTree() {
            if (!scope.vm.lyrParam) return;

            scope.vm.overlays_tree = {};
            for (var lyr in scope.vm.lyrParam) {
                scope.vm.overlays_tree[scope.vm.lyrParam[lyr].name] = [true, scope.vm.lyrParam[lyr].download];
            }
        }
    }

    /////////////////////////////
    // Remove and add layers by click
    function LayersControl(scope) {
        return layersControl;

        function layersControl(lyr) {
			if (lyr.status) {
				scope.vm.map.addLayer(lyr.lyr);
			} else {
				scope.vm.map.removeLayer(lyr.lyr);
			}
        }
    }
    
    // Remove or Add Layer by click - Layers added from SDI
    function GeoserverLyrControl (scope) {
    	return geoserverLyrControl;
    	
    	function geoserverLyrControl (lyr) {
    		if (!lyr.fields.status) {
    			scope.vm.lyr_geoserver[lyr.fields.table].forEach(function(d) {
    				scope.vm.map.removeLayer(d);
    			});
    			lyr.fields.status = false;
    		} else {
    			scope.vm.lyr_geoserver[lyr.fields.table].forEach(function(d) {
    				scope.vm.map.addLayer(d);
    			});
    			lyr.fields.status = true;
    		}
    	}
    };
    
    /////////////////////////////
    // Get Tree Layers from Themes table and Layers Table
    function GetOverlaysByTheme(scope) {
    	return getOverlaysByTheme;
    	
    	function getOverlaysByTheme(cells) {
    		if (!cells) return;
    		
    		var lyrThemes = ThemesTable.query();
    		var lyrTable = LayersTable.query();
    		var settings = Settings.query();
    		
    		$q.all([
    			lyrThemes.$promise,
    			lyrTable.$promise,
    			settings.$promise
    		]).then(function () {
    			scope.vm.layerTree = getRootThemes(lyrThemes);
    			getChildrenThemes(lyrThemes, scope.vm.layerTree);
    			addLayersToThemes(scope.vm.layerTree, lyrTable);
    			addLayersToMap(scope.vm.layerTree, cells, settings);
    		});
    	}
    	
    	// Get root nodes
    	function getRootThemes(data, root_id) {
    		root_id = root_id === undefined ? false : root_id;
    		var root_array = [];
    		
    		data.forEach(function (d) {
    			if (!d.fields.parent || d.fields.parent === root_id) {
    				d.fields['status'] = false;
    				d.fields['css'] = 'href_active';
    				root_array.push(d);
    			}
    		});
    		
    		return root_array;
    	}
    	
    	// Get children nodes
    	function getChildrenThemes(data, root_data) {
    		root_data.forEach(function(d) {
    			data.forEach(function(e) {
    				if (d.pk === e.fields.parent) {
    					e.fields['status'] = false;
    					e.fields['css'] = 'href_active';
    					if (d.fields.child) {
    						d.fields.child.push(e);
    					} else {
    						d.fields['child'] = [e];
    					}
    					
    					// Do it for all existent sub-children
    					getChildrenThemes(data, d.fields.child);
    				}
    			});
    		});
    	}
    	
    	// Add layers to themes
    	function addLayersToThemes(themes, layers) {
    		themes.forEach(function (theme) {
    			layers.forEach(function (layer) {
    				if (theme.pk === layer.fields.theme) {
    					layer.fields['status'] = false;
    					layer.fields['css'] = 'href_active';
    					if (!theme.fields.layers) {
    						theme.fields['layers'] = [layer];
    					} else {
    						theme.fields.layers.push(layer);
    					}
    				}
    			});
    			
    			if (!!theme.fields.child) {
					addLayersToThemes(theme.fields.child, layers);
				}
    		});
    	}
    	
    	// Add layers to MAP
    	function addLayersToMap(themes, cells, set) {
            themes.forEach(function (theme) {
                if (theme.fields.layers) {
                    addLayers(theme.fields.layers, cells, set);
                }

                if (theme.fields.child) {
                    addLayersToMap(theme.fields.child, cells, set);
                }
            });
        }
    	
    	function addLayers(layers, cells_str, SETTINGS) {
            if (!layers) return;
            
            var host = SETTINGS[0].GEOSERVER.HOST;
            var port = SETTINGS[0].GEOSERVER.PORT;
            var lst_cells = cells_str.split(';');
            var protocol = SETTINGS[0].GEOSERVER.PROTOCOL;

            layers.forEach(function(d) {
            	scope.vm.lyr_geoserver[d.fields.table] = [];
                lst_cells.forEach(function(c) {
                    var wmsLayer = L.tileLayer.wms(
                        protocol + '://' + host + ':' + port + '/geoserver/ows?', {
                            layers: 'expvgi_gs:'+ d.fields.table + '_' + c,
                            transparent: true,
                            format: 'image/png',
                            styles: d.fields.style
                    });

                    scope.vm.lyr_geoserver[d.fields.table].push(wmsLayer);
                });
            });
        }
    }
}


})();