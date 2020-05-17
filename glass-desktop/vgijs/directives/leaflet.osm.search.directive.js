(function () {"use strict";

angular
	.module('vgijs.directives')
	.directive('vgijsOsmSearch', leafletSearch);

leafletSearch.$inject = ['$http', '$document'];

function leafletSearch($http, $document) {
	var directive = {
		restrict: 'E',
		replace: false,
		transclude: true,
		templateUrl: '/static/vgi-angular/leafletOsmSearch.html',
		scope: {
			mapcenter : '='
		},
		link: link,
		controller: leafletSearchController,
		controllerAs: 'vm',
		binToController: true
	};

	return directive;

	function link(scope, iElement, iAttrs) {
		// Home made search control
		scope.vm.searchbox = false;
		scope.vm.searchKeyword = undefined;
		scope.vm.locations = false;
		scope.vm.clickOnInput = false;
		scope.vm.places = false;
		scope.vm.placeholder = 'Type a place name';

		// Function to activate search input box
		scope.vm.searchOn = function() {
			scope.vm.searchbox ^= true;
		};

		// Clear dropdow with finded places
        $document.on('click', function() {
            if (!scope.vm.locations) return;
            
            scope.$apply(function () {
                scope.vm.locations = false;
            	scope.vm.searchKeyword = undefined;
            });
        });

    	// Check keyword introduction
    	scope.$watch('vm.searchKeyword', SearchPlacesOSM(), true);

    	// Search for data in OSM using a keyword
    	function SearchPlacesOSM() {
        	return searchForSomeplace;
            
        	function searchForSomeplace() {
            	if (!scope.vm.searchKeyword) return;
            	getPlacesOSM(scope.vm.searchKeyword).then(function(d) {
                	scope.vm.locations = d;
            	});
        	};

        	function getPlacesOSM(place) {
        		var promise = $http({
            		method: 'GET',
            		url: 'https://nominatim.openstreetmap.org/search?format=json&accept-language=en&q=' + place
        		}).then(function (response) {
            		var json_response = response.data;
            		return response.data;
        		});
        
       			return promise;
   			};
    	};

    	// Show places located
    	scope.$watch('vm.locations', ShowPlacesFinded(), true);

		function ShowPlacesFinded() {
        	return showPlacesFinded;
            
        	function showPlacesFinded() {
            	if (!scope.vm.locations) return;
                
            	scope.vm.places = [];
            	for (var i=0; i < scope.vm.locations.length; i++) {
                	scope.vm.places.push({
                    	'name': scope.vm.locations[i].display_name,
                    	'lat': scope.vm.locations[i].lat,
                    	'lng': scope.vm.locations[i].lon
                	});
            	};
        	};
    	};

    	// Function to update view
		scope.vm.zoomToLocation = ZoomToLocation();

		// Zoom to the locations finded
    	function ZoomToLocation() {
        	return zoomToLocation;
        
        	function zoomToLocation(lat, lng) {
            	scope.vm.locations = false;
            	scope.vm.searchKeyword = undefined;
            	scope.vm.searchbox = false;
            	var search_checkbox = angular.element(
                	document.querySelector( '#search-dropdown' )
            	);
            	search_checkbox.removeClass('active');
            
            	scope.mapcenter.lat = lat;
            	scope.mapcenter.lng = lng;
            	scope.mapcenter.zoom = 13;
        	};
    	};
	};
};

leafletSearchController.$inject = ['$scope'];

function leafletSearchController($scope) {
	/* jshint validthis: true */
	var vm = this;
}

})();