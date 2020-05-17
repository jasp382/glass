(function () {"use strict";

angular
	.module('jsidejs.components')
	.directive('addLyrStudyCase', addLyrStudyCase);

addLyrStudyCase.$inject = [
	'$q', 'GetDataset', 'GetDatasetCols', 'YearsTable','Indicators'];


function addLyrStudyCase($q, GetDataset, GetDatasetCols, YearsTable, Indicators) {
	var directive = {
		restrict         : 'E',
		replace          : false,
		transclude       : true,
		templateUrl      : '/static/partials/add-lyr-study-case.html',
		scope : {
			rqstfid  : '=',
			scaledif : '='
		},
		link             : link,
		controller       : addLyrStudyCaseController,
		controllerAs     : 'vm',
		bindToController : true
	};
	
	return directive;
	
	function link (scope, iElement, iAttrs) {
		///////////////////////   Get Datasets List   /////////////////////
		scope.vm.get_dataset = true;
		scope.vm.datasets = undefined;
		scope.vm.cols     = undefined;
		scope.vm.years    = undefined;
		scope.vm.indicators = undefined;
		
		scope.$watch('vm.get_dataset', GetDatasetList(), true);
		
		function GetDatasetList() {
			return getDatasetList();
			
			function getDatasetList() {
				var data  = GetDataset.query({fid:scope.vm.rqstfid}),
					cols  = GetDatasetCols.query({
						fid:scope.vm.rqstfid, ctx: 0}),
					cols_ctx = GetDatasetCols.query({
						fid:scope.vm.rqstfid, ctx: 1}),
					indi  = Indicators.query(),
					years = YearsTable.query();
				
				$q.all([
					data.$promise,
					cols.$promise,
					cols_ctx.$promise,
					indi.$promise,
					years.$promise
				]).then(function () {
					scope.vm.datasets   = data[0];
					scope.vm.cols       = cols;
					scope.vm.cols_ctx   = cols_ctx;
					scope.vm.indicators = indi;
					scope.vm.years      = years;
				});
			};
		};
	};
};

addLyrStudyCaseController.$inject = ['$scope'];

function addLyrStudyCaseController($scope) {
	/* jshint validthis: true */
	var vm = this;
};

})();