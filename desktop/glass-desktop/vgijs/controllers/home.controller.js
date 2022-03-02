(function () {'use strict';

angular
	.module('vgijs.controllers')
	.controller('VgiHomeController', VgiHomeController);

VgiHomeController.$inject = [
	'$scope', '$window', '$location', '$anchorScroll', 'deviceDetector'
];

function VgiHomeController($scope, $window, $location, $anchorScroll, deviceDetector) {
	var homeVm = this;
	
	homeVm.browser = deviceDetector.browser;
    
    if (homeVm.browser !== 'chrome') {
    	$window.location.href = '/expvgi/?browser=1'
    };
	
	homeVm.gotoElement = function(idElement) {
		// set the location.hash to the id of
		// the element you wish to scroll to.
		$location.hash(idElement);
		// call $anchorScroll()
		$anchorScroll();
	}
};

})();