(function () {'use strict';

angular
	.module('vgijs.services')
	.service('LeafletDraw', LeafletDraw);

LeafletDraw.$inject = ['L', 'LeafletControls'];

function LeafletDraw(L, LeafletControls) {
	var service = {
		drawCircle     : DrawingCircle,
		circleEvent    : CircleEvent,
		drawRectangle  : DrawingRectangle,
		rectangleEvent : RectangleEvent
	};
	
	return service;
	
	/////////////////////////////
	
	function DrawingCircle(scope) {
		return drawingCircle;
		
		function drawingCircle(isDraw) {
			if (!isDraw) return;
			
			new L.Draw.Circle(
				scope.vm.map,
				{
					metric       : true,
					feet         : false,
					shapeOptions : {color: 'red'}
				}
			).enable()
		}
	}
	
	/////////////////////////////
	
	function CircleEvent(scope) {
		return circleEvent;
		
		function circleEvent(event) {
			if (scope.vm.zoom_in || scope.vm.zoom_out) {
				LeafletControls.executeZoom(scope, event);
			} else {
				if (scope.vm.draw_lyr) {
					scope.vm.drawnItems.removeLayer(scope.vm.draw_lyr);
				}
				
				scope.vm.draw_lyr = event.layer;
				scope.vm.drawnItems.addLayer(scope.vm.draw_lyr);
				
				scope.$apply(function () {
					scope.vm.settings.draw.edit = false;
					
					var lat_long = scope.vm.draw_lyr.getLatLng();
					var radius = scope.vm.draw_lyr.getRadius();
					
					scope.vm.settings.draw.output = String(lat_long.lat) + ',' +
						String(lat_long.lng) + ';' + String(radius);
					
					scope.vm.settings.draw.radius = radius;
				});
			}
		}
	}
	
	/////////////////////////////
	
	function DrawingRectangle(scope) {
		return drawingRectangle;
		
		function drawingRectangle(isDraw) {
			if (!isDraw) return;
			
			new L.Draw.Rectangle(
				scope.vm.map,
				{
					metric       : true,
					feet         : false,
					shapeOptions : {color: 'red'}
				}
			).enable()
		}
	}
	
	/////////////////////////////
	
	function RectangleEvent(scope) {
		return rectangleEvent;
		
		function rectangleEvent(event) {
			if (scope.vm.zoom_in || scope.vm.zoom_out) {
				LeafletControls.executeZoom(scope, event);
			} else {
				if (scope.vm.draw_lyr) {
					scope.vm.drawnItems.removeLayer(scope.vm.draw_lyr);
				}
				
				scope.vm.draw_lyr = event.layer;
				scope.vm.drawnItems.addLayer(scope.vm.draw_lyr);
				
				var bounds = scope.vm.draw_lyr.getBounds();
				
				scope.$apply(function () {
					scope.vm.settings.draw.edit = false;
					
					scope.vm.settings.draw.output = String(bounds._southWest.lng) + ',' +  String(bounds._northEast.lat) + ';' +
						String(bounds._northEast.lng) + ', ' + String(bounds._northEast.lat) + ';' +
						String(bounds._northEast.lng) + ', ' + String(bounds._southWest.lat) + ';' +
						String(bounds._southWest.lng) + ', ' + String(bounds._southWest.lat) + ';' +
						String(bounds._southWest.lng) + ', ' + String(bounds._northEast.lat);
				});
			}
		}
	}
}

})();