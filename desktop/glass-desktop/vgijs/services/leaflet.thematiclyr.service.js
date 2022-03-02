(function () {'use strict';

angular
    .module('vgijs.services')
    .service('LeafletThematicLayers', LeafletDef);

LeafletDef.$inject = ['L'];

function LeafletDef(L) {
    var service = {
        getLayer: getLyr
    };
    
    return service;
    
    /////////////////////////////
    
    function getLyr(layerTag, geodata, scopeArray, srcUrl) {
        var lyrRepo = layerRepository();
        
        var layerObj = lyrRepo[layerTag];
        return layerObj();

        function layerRepository() {
            return {
				'areai'        : simpleBoundary,
                'boundary'     : simpleBoundary,
                'osm2lulc'     : osmtolulc,
                'pnt_facebook' : facebook_as_point,
                'pnt_flickr'   : flickr_as_point,
                'pnt_twitter'  : twitter_as_point,
                'pnt_youtube'  : youtube_as_point,
                'sdi_grid'     : selectByClick
            }
        };

        ///////////// BOUNDARY LAYER /////////////
        function simpleBoundary () {
            return L.geoJson(geodata, {
                style : function (feature) {
                    return {
                        opacity: 1,
                        dashArray: '3',
                        fillOpacity: 0,
                        color: 'black'
                    }
                }
            });
        };
        ///////////// END LAYER /////////////

        ///////////// OSM2LULC PRODUCT LAYER /////////////
        function get_lulc_cls (nomenclature) {
            if (nomenclature === 'lulc_ua') {
                return {
                    11: "Urban Fabric",
                    12: "Industrial, commercial, public, military, private, and transport units",
                    13: "Mine, dump and construction sites",
                    14: "Artifical non-agricutural vegetated areas",
                    2: "Agricultural, semi-natural areas, wetlands",
                    3: "Forests",
                    5: "Water",
                    255: "NoData"
                }
            } else if (nomenclature === 'lulc_clc') {
                return {
                    11: "Urban Fabric",
                    12: "Industrial, commercial, public, military, private, and transport units",
                    13: "Mine, dump and construction sites",
                    14: "Artifical non-agricutural vegetated areas",
                    2: "Agricultural areas",
                    21: "Arable Land",
                    22: "Permanent crops",
                    23: "Pastures",
                    24: "Heterogeneous",
                    31: "Forests",
                    32: "Scrub and/or herbaceous vegetation associations",
                    33: "Open spaces with little or no vegetation",
                    4: "Wetlands",
                    5: "Water",
                    255: "NoData"
                }
            } else if (nomenclature === 'lulc_30') {
                return {
                    10: "Cultivated land",
                    20: "Forest",
                    30: "Grassland",
                    40: "Scrubland",
                    50: "Wetland",
                    60: "Water bodies",
                    70: "Tundra",
                    80: "Artificial surfaces",
                    90: "Bareland",
                    100: "Permanent snow/ice",
                    255: "NoData"
                }
            }
        };

        function getColorLulc(d) {
            return d == 11 ? '#e6004d' :
                d == 12 ? '#cc4df2' :
                d == 13 ? '#986b58' :
                d == 14 ? '#a7bd39' :
                d == 2 ? '#fff9ba' :
                d == 3 ? '#016f45' :
                d == 5 ? '#b9e5fa' :
                d == 4 ? '#4d4dff' :
                d == 21 ? '#ffff00' :
                d == 22 ? '#e68000' :
                d == 23 ? '#E6E64D' :
                d == 24 ? '#e6cc4d' :
                d == 31 ? '#016f45' :
                d == 32 ? '#a6f200' :
                d == 33 ? '#e6e6e6' :
                d == 80 ? '#fe0000' :
                d == 60 ? '#00a8e6' :
                d == 50 ? '#02fdc7' :
                d == 10 ? '#fff9ba' :
                d == 30 ? '#70a800' :
                d == 20 ? '#016f45' :
                d == 40 ? '#e69900' :
                d == 70 ? '#646432' :
                d == 90 ? '#cacaca' :
                d == 100 ? '#d3edfb' :
                '#d3d3d3';
        };

        function osmtolulc() {
            var __topology = topojson.topology(
                {collection: geodata}
            );

            var lyr = omnivore.topojson.parse(__topology);

            lyr.setStyle(function (feature) {
                return {
                    fillColor: getColorLulc(feature.properties.value),
                    weight: 2,
                    opacity: 1,
                    color: false,
                    dashArray: '3',
                    fillOpacity: 1
                };
            });

            lyr.eachLayer(function (layer) {
                var lulc_cls = get_lulc_cls(layerTag);

                var popup = "<b>CODE: </b>" +
                    String(layer.feature.properties.value) +
                    "<br><b>CLASS: </b>" +
                    lulc_cls[layer.feature.properties.value];

                lyr.bindPopup(popup);
            });
        };
        ///////////// END LAYER /////////////

        ///////////// FACEBOOK AS POINT LAYER /////////////
        function facebook_as_point () {
            var baseLyr = L.markerClusterGroup();

            var lyr = L.geoJson(geodata, {
                pointToLayer: function (feature, latlng) {
                    var f_icon = L.icon({
                        iconUrl: '/static/vgijs/img/maps/facebook.png',
                        iconSize: [25,30],
                        iconAnchor: [12.5,30],
                        popupAnchor: [0,-30]
                    });

                    var __lyr = L.marker(latlng, {icon: f_icon});

                    __lyr.bindPopup(popupStringBasedLayerFeatures(
                        feature, "Facebook", "DarkBlue"
                    ));

                    return __lyr;
                },
                onEachFeature: function (feature, layer) {
                    layer.addTo(baseLyr);
                }
            });

            return baseLyr;
        };
        ///////////// END LAYER /////////////

        ///////////// FLICKR AS POINT LAYER /////////////
        function flickr_as_point() {
            var baseLyr = L.markerClusterGroup();

            var lyr = L.geoJson(geodata, {
                pointToLayer: function (feature, latlng) {
                    var f_icon = L.icon({
                        iconUrl: '/static/vgijs/img/maps/flickr25x30.png',
                        iconSize: [25,30],
                        iconAnchor: [12.5,30],
                        popupAnchor: [0,-30]
                    });

                    var __lyr = L.marker(latlng, {icon: f_icon});

                    __lyr.bindPopup(popupStringBasedLayerFeatures(
                        feature, "Flickr", "DeepPink"
                    ));

                    return __lyr;
                },
                onEachFeature: function (feature, layer) {
                    layer.addTo(baseLyr);
                }
            });

            return baseLyr;
        };

        ///////////// END LAYER /////////////

        ///////////// TWITTER AS POINT LAYER /////////////
        function twitter_as_point() {
            var baseLyr = L.markerClusterGroup();

            var lyr = L.geoJson(geodata, {
                pointToLayer: function (feature, latlng) {
                    var f_icon = L.icon({
                        iconUrl: '/static/vgijs/img/maps/twitter25x30.png',
                        iconSize: [25,30],
                        iconAnchor: [12.5,30],
                        popupAnchor: [0,-30]
                    });

                    var __lyr = L.marker(latlng, {icon: f_icon});

                    __lyr.bindPopup(popupStringBasedLayerFeatures(
                        feature, "Twitter", "DeepSkyBlue"
                    ));

                    return __lyr;
                },
                onEachFeature: function (feature, layer) {
                    layer.addTo(baseLyr);
                }
            });

            return baseLyr;
        };
        ///////////// END LAYER /////////////

        ///////////// YOUTUBE AS POINT LAYER /////////////
        function youtube_as_point() {
            var baseLyr = L.markerClusterGroup();

            var lyr = L.geoJson(geodata, {
                pointToLayer: function (feature, latlng) {
                    var f_icon = L.icon({
                        iconUrl: '/static/vgijs/img/maps/youtube25x30.png',
                        iconSize: [25,30],
                        iconAnchor: [12.5,30],
                        popupAnchor: [0,-30]
                    });

                    var __lyr = L.marker(latlng, {icon: f_icon});

                    __lyr.bindPopup(popupStringBasedLayerFeatures(
                        feature, "Youtube", "DeepRed"
                    ));

                    return __lyr;
                },
                onEachFeature: function (feature, layer) {
                    layer.addTo(baseLyr)
                }
            });
            
            return baseLyr;
        }
        ///////////// END LAYER /////////////

        ///////////// SDI GRID LAYER /////////////
        function selectByClick() {
            var topo = true;

            if (!topo) {
                var lyr = L.geoJson(geodata, {
                    style: function (feature) {
                        return {
                            opacity: 1,
                            dashArray: '3',
                            fillOpacity: 0,
                            color: 'black'
                        }
                    },
                    onEachFeature: featSelect
                });
            } else {
                var ghostLyr = L.geoJson(null, {
                    style: function (feature) {
                        return {
                            opacity: 1,
                            dashArray: '3',
                            fillOpacity: 0,
                            color: 'black'
                        }
                    },
                    onEachFeature: featSelect
                });
                var lyr = omnivore.topojson(srcUrl, null, ghostLyr);
            }

            return lyr;
        };

        function featClicked(e) {
            var featLyr = e.target;
            var cellsSel = scopeArray.vm.settings.click.output;
            var cellId = String(e.target.feature.properties.id_grid);
            if (cellsSel.indexOf(cellId) > -1) {
                featLyr.setStyle({
                    opacity: 1,
                    fillOpacity: 0,
                    dashArray: '3',
                    color: 'black',
                });

                scopeArray.$apply(function () {
                    if (cellsSel.indexOf(';' + cellId) > -1) {
                        cellsSel.replace(';' + cellId, '');
                    } else {
                        if (cellsSel.indexOf(cellId + ';') > -1) {
                            scopeArray.vm.settings.click.output = cellsSel.replace(cellId + ';', '');
                        } else {
                            scopeArray.vm.settings.click.output = cellsSel.replace(cellId, '');
                        }
                    }
                });
            } else {
                featLyr.setStyle({
                    color: 'green',
                    dashArray: '3',
                    fillOpacity: 0.7
                });

                scopeArray.$apply(function () {
                    if (cellsSel === '') {
                        scopeArray.vm.settings.click.output = cellId;
                    } else {
                        scopeArray.vm.settings.click.output += ';' + cellId;
                    }
                });
            }
        }

        function featSelect(feature, layer) {
            layer.on({ click: featClicked });
        };
        ///////////// END LAYER /////////////
    }

    // Auxiliary functions
    function popupStringBasedLayerFeatures(feat, title, color) {
        var str_popup = "<b style='color:" + color + ";'>" + title + "</b><br>";
        
        var feat_html;
        
        for (var field in feat.properties) {
            if (feat.properties.hasOwnProperty(field)) {
                if (!feat.properties[field]) {
                    feat_html = 'null';
                } else if (String(feat.properties[field]).substring(0,4) === 'http') {
                    feat_html = "<a href='" + feat.properties[field] + "' target='_blank'>Click</a>";
                } else {
                    feat_html = feat.properties[field];
                }
                
                str_popup += "<b>" + field + ": </b>" +
                    feat_html +
                    "<br>";
            }
        }
        
        return str_popup;
    }
}

})();