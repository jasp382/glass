(function () {'use strict';

angular
	.module('vgijs.controllers')
	.controller('FirelocReportController', FirelocReportController);

FirelocReportController.$inject = ['$scope'];

function FirelocReportController($scope) {
	var mapVm = this;
	
	mapVm.settings = {
		zoom: {
			min: 1,
			max: 20
		},
		form : {
			fname   : undefined,
			lname   : undefined,
			subject : undefined,
			latlng  : undefined
		}
	};
}

})();