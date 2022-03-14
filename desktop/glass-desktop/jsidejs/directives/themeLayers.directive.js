(function () {"use strict";

angular
	.module('jsidejs.directives')
	.directive('manageThemeLayer', manageThemeLayer);

manageThemeLayer.$inject = ['$q', 'Indicators', 'GetDataset'];

function manageThemeLayer($q, Indicators, GetDataset) {
	var directive = {
		restrict         : 'E',
		replace          : false,
		transclude       : true,
		templateUrl      : '/static/lyrtheme-manage.html',
		scope : {
			wtodo  : '=',
			rqstid : '='
		},
		link             : link,
		controller       : manageThemeLayerController,
		controllerAs     : 'vm',
		bindToController : true
	};
	
	return directive;
	
	function link(scope, iElement, iAttrs) {
		// See what todo
		if (scope.vm.wtodo === 203) {
			scope.vm.needIndicators = false;
			scope.vm.colsFileForm   = true;
		} else {
			scope.vm.needIndicators = true;
			scope.vm.colsFileForm   = undefined;
		}
		///////////////////////////////////////
		scope.vm.addIndicator  = false;
		scope.vm.addIndicators = false;
		
		scope.vm.enableAddIndicator = function (howmany) {
			if (howmany === 'many') {
				scope.vm.addIndicators = true;
			} else {
				scope.vm.addIndicator = true;
			};
		};
		
		// Get Indicators List
		scope.vm.indicators = undefined;
		
		scope.$watch('vm.needIndicators', GetIndicators(), true);
		
		function GetIndicators() {
			return getIndicators;
			
			function getIndicators () {
				if (!scope.vm.needIndicators) return;
				
				var rawIndicators = Indicators.query()
				
				$q.all([
					rawIndicators.$promise
				]).then(function () {
					scope.vm.indicators = rawIndicators;
				});
			};
		};
		//////////////////////////////////////////////////////////////
		// Get Columns in Data File
		scope.$watch('vm.colsFileForm', GetColumnsFile(), true);
		
		function GetColumnsFile () {
			return getColumnsFile;
			
			function getColumnsFile () {
				if (!scope.vm.colsFileForm) return;
				
				var raw_data = GetDataset.query({fid : scope.vm.rqstid});
				
				$q.all([
					raw_data.$promise
				]).then(function () {
					scope.vm.dataset = raw_data[0];
				});
			};
		};
	};
};

manageThemeLayerController.$inject = ['$scope'];

function manageThemeLayerController($scope) {
	/* jshint validthis: true */
	var vm = this;
};

})();