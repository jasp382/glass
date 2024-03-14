var mymap = L.map('map');

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
	maxZoom: 18,
	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
		'<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
		'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
	id: 'mapbox/streets-v11',
	tileSize: 512,
	zoomOffset: -1
}).addTo(mymap);

// Add DEM WMS
var wms_url = '/api/wms/cwsig?';

var wmsLayer = L.tileLayer.wms(wms_url, {
    layers : 'dem_coimbra',
    format : 'image/png',
    transparent: true,
    styles : 'dem_style2'
});

mymap.addLayer(wmsLayer);

// Get and Set Map Extent
var url_extent = '/api/extent/cwsig/dem_coimbra/';
var extent = undefined;

$(document).ready(function () {
	$.getJSON(url_extent, function(result) {
		extent = result;

		var topleft = L.latLng(extent['max_y'], extent['min_x']),
			lowerright = L.latLng(extent['min_y'], extent['max_x']);
		
		var bounds = L.latLngBounds(topleft, lowerright);

		mymap.fitBounds(bounds);
	});
});

// Add Point Layer
var url_lyr = '/api/wfs/cwsig/osm_points/?count=1000';

// Auxiliary functions
function popupStringBasedLayerFeatures(feat) {
	var str_popup = "<b style='color:DeepSkyBlue;'>OSM Points</b><br>";
	
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
};

$(document).ready(function () {
	$.getJSON(url_lyr, function(gjson) {
        // Marker Cluster layer
        var baseLyr = L.markerClusterGroup();

        // Create Layer
        var gjson_lyr = L.geoJSON(gjson, {
            pointToLayer: function (feature, latlng) {
                var f_icon = L.icon({
                    iconUrl: '/static/map-pin.svg',
                    iconSize: [25, 30],
                    iconAnchor: [12.5, 30],
                    popupAnchor: [0, -30]
                });

                var feat = L.marker(latlng, {icon: f_icon});

                feat.bindPopup(
                    popupStringBasedLayerFeatures(feature)
                );

                return feat;
            },
			onEachFeature: function (feat, lyr) {
				lyr.addTo(baseLyr);
			}
        });

        mymap.addLayer(baseLyr);
    });
});

// Add Roads using filter
var motorway_url = '/api/wfs/cwsig/osm_roads/?val=motorway&attr=highway',
    primary_url  = '/api/wfs/cwsig/osm_roads/?val=primary&attr=highway';

function get_color (d) {
    return d === 'motorway' ? 'black' : 'blue';
};

$(document).ready(function () {
    $.getJSON(motorway_url, function(gjson) {
        var motor_lyr = L.geoJSON(gjson, {
            style : function set_style(feature) {
                return {
                    opacity : 1,
                    color : get_color(feature.properties.highway)
                }
            }
        });

        mymap.addLayer(motor_lyr);
    });
});

$(document).ready(function () {
    $.getJSON(primary_url, function(gjson) {
        var prim_lyr = L.geoJSON(gjson, {
            style : function set_style(feature) {
                return {
                    opacity : 1,
                    color : get_color(feature.properties.highway)
                }
            }
        });

        mymap.addLayer(prim_lyr);
    });
});

// Get Feature Info
var mdtinfo = '/api/featinfo/cwsig/dem_coimbra/';

mymap.on('click', function (event) {
	var clickPnt = mymap.latLngToContainerPoint(event.latlng, mymap.getZoom()),
		size     = mymap.getSize(),
		mdtinfo  = '/api/featinfo/cwsig/dem_coimbra/?WIDTH=' + String(size.x) +
			'&HEIGHT=' + String(size.y) + '&X=' + String(clickPnt.x) +
			'&Y=' + String(clickPnt.y) +
			'&BBOX=' + String(mymap.getBounds().toBBoxString());
		
	$(document).ready(function () {
		$.getJSON(mdtinfo, function (data) {
			var popup = L.popup(),
				feat  = data.features[0];
			
			if (!feat) return;
					
			popup
				.setLatLng(event.latlng)
				.setContent(
					"<p><b>Altitude: </b>" + String(feat.properties.GRAY_INDEX) + '</p>'
				).openOn(mymap);
		});
	});
});