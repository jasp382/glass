(function () {'use strict';

angular
	.module('vgijs.controllers')
	.controller('VgiHeaderContent', VgiHeaderContent);

VgiHeaderContent.$inject = [
	'$scope', '$location', '$anchorScroll'
];

function VgiHeaderContent($scope, $location, $anchorScroll) {
	var headVm = this;

	headVm.dropdowns = {
		services : false,
		partners : false,
		about    : false,
		credits  : false,
		help     : false
	};

	headVm.toggleDropdown = function (dropref) {
		headVm.dropdowns[dropref] ^= true;
	};
	
	headVm.gotoElement = function(idElement) {
		// set the location.hash to the id of
		// the element you wish to scroll to.
		$location.hash(idElement);
		// call $anchorScroll()
		$anchorScroll();
	}

	// TODO: Deal with active
};

})();