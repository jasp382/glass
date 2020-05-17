(function () {'use strict';

angular
	.module('jsidejs.constants')
	.constant('L', L)
	.constant('d3', d3)
	.constant('GOOGLE_EARTH', 
		'http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}')
	.constant('GOOGLE_MAPS',
		'http://www.google.cn/maps/vt?lyrs=m@231000000&gl=cn&x={x}&y={y}&z={z}')
	.constant('OSM_URL', 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
	.constant('OSM_ATTRIBUTION',
		'Map data � <a href="http://openstreetmap.org">OpenStreetMap</a> contributors')
	.constant('OSM_SEARCH_URL', 'http://nominatim.openstreetmap.org/' + 
		'search?format=json&accept-language=en&q={s}'
	)
	.constant('BASEMAP_OPTIONS', {
        "Mapbox Streets"      : "MAPBOX_STREETS",
        "OpenStreetMap"       : "OSM",
        "Google Earth"        : "GOOGLE_EARTH",
        "Google Maps"         : "GOOGLE_MAPS",
        "Topographic"         : "Topographic",
        "ESRI Streets"        : "Streets",
        "National Geographic" : "NationalGeographic",
        "Oceans"              : "Oceans",
        "Gray"                : "Gray",
        "Dark Gray"           : "DarkGray",
        "ESRI Imagery"        : "Imagery",
        "Shaded Relief"       : "ShadedRelief"
    })
    .constant('BASEMAPS_TREE', {
        "Mapbox": [
            {'open': true, 'css': 'href_active'},
            {"Mapbox Streets": true}
        ],
        "Google": [
            {'open': true, 'css': 'href_active'},
            {
                "Google Earth": false,
                "Google Maps": false
            }
        ],
        "OpenStreetMap": [
            {'open': true, 'css': 'href_active'},
            {
                "OpenStreetMap": false
            }
        ],
        "ESRI": [
            {'open': false, 'css': 'href_active'},
            {
                "Topographic": false,
                "ESRI Streets": false,
                "National Geographic": false,
                "Oceans": false,
                "Gray": false,
                "Dark Gray" : false,
                "ESRI Imagery" : false,
                "Shaded Relief": false
            }
        ],
    });

})();