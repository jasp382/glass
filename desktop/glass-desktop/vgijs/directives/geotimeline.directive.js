(function () {"use strict";

angular
	.module('vgijs.directives')
	.directive('expvgiGeoTimeLine', expvgiGeoTimeLine);

expvgiGeoTimeLine.$inject = [];

function expvgiGeoTimeLine() {
	var directive = {
		restrict : 'E',
		replace  : false,
		transclude :  true,
		templateUrl : '/static/html/GeoTimeLine.html',
		scope : {
			eventid : '='
		},
		link : link,
		controller : expvgiGeoTimeLineController,
		controllerAs : 'vm',
		bindToController : true
	};
	
	return directive;
	
	function link(scope, iElement, iAttrs) {
		scope.vm.tmp = undefined;
	};
}

expvgiGeoTimeLineController.$inject = ['$scope'];

function expvgiGeoTimeLineController ($scope) {
	/* jshint validthis: true */
	var vm = this;
};

})();