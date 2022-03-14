(function () {"use strict";

angular
	.module('jsidejs.directives')
	.directive('manageStudyCases', manageStudyCases);

manageStudyCases.$inject = [
	'$window',
	'$q', 'StudyCases', 'LayersTbl', 'PntLyrTbl', 'PolyLyrTbl'
];

function manageStudyCases(
	$window, $q, StudyCases, LayersTbl, PntLyrTbl, PolyLyrTbl) {
	var directive = {
		restrict         : 'E',
		replace          : false,
		transclude       : true,
		templateUrl      : '/static/study-cases.html',
		scope : {
			wtodo  : '=',
			rqstid : '=',
			ctxdif : '='
		},
		link             : link,
		controller       : manageStudyCasesController,
		controllerAs     : 'vm',
		bindToController : true
	};
	
	return directive;
	
	function link(scope, iElement, iAttrs) {
		// O que a pagina deve mostrar
		if (scope.vm.wtodo === 303) {
			scope.vm.initial    = false;
			scope.vm.addStatLyr = true;
		} else {
			scope.vm.initial    = true;
			scope.vm.addStatLyr = false;
		};
		
		/////////////////////////   List Study Cases   ///////////////////////
		scope.vm.studyCases = undefined;
		scope.vm.getCases = true;
		
		scope.$watch('vm.getCases', GetStudyCases(), true);
		
		function GetStudyCases() {
			return getStudyCases();
			
			function getStudyCases() {
				var rawCases = StudyCases.query();
				
				$q.all([
					rawCases.$promise
				]).then(function () {
					scope.vm.studyCases = rawCases;
				});
			};
		};
		
		/////////////////////////   Activate data list   ///////////////////////
		scope.vm.caseSelected   = undefined;
		scope.vm.caseIndicators = undefined;
		scope.vm.casePntLyr     = undefined;
		scope.vm.casePolyLyr    = undefined;
		
		scope.vm.showStudyCaseInfo = function (clickCase) {
			scope.vm.caseSelected = clickCase;
			scope.vm.addNewLayer = false;
		};
		
		// Get Layers in Study Case
		scope.$watch('vm.caseSelected', GetLayers, true);
		
		function GetLayers() {
			if (!scope.vm.caseSelected) return;
				
			var rawIndicators = LayersTbl.query({
					case : scope.vm.caseSelected.fid
				}),
				rawPoints     = PntLyrTbl.query({
					case : scope.vm.caseSelected.fid
				}),
				rawPolygons = PolyLyrTbl.query({
					case : scope.vm.caseSelected.fid
				});
				
			$q.all([
				rawIndicators.$promise, rawPoints.$promise,
				rawPolygons
			]).then(function () {
				if (rawIndicators.length) {
					scope.vm.caseIndicators = rawIndicators;
				};
				
				if (rawPoints.length) {
					scope.vm.casePntLyr     = rawPoints;
				};

				if (rawPolygons.length) {
					scope.vm.casePolyLyr = rawPolygons
				}
			});
		};

		// See list of Layers
		scope.vm.indicatorsOpen = false;

		scope.vm.openIndicatorsList = function () {
			scope.vm.indicatorsOpen ^= true;
		};

		scope.vm.pointsOpen = false;
		scope.vm.openPointsList = function () {
			scope.vm.pointsOpen ^= true;
		};

		scope.vm.polygonsOpen = false;
		scope.vm.openPolygonsList = function () {
			scope.vm.polygonsOpen ^= true;
		};
		
		///////////////////////   Add/Edit Study Cases   ///////////////////////
		scope.vm.addStudyCases = false;
		scope.vm.editStudyCase = false;
		
		// Enable form to add study case
		scope.vm.enableAddForm = function (w, scase) {
			if (w === 'edit'){
				scope.vm.editStudyCase = scase;
			} else {
				scope.vm.addStudyCases ^= true;
			}
			scope.vm.addNewLayer   = false;
		};
		
		/////////////////////////   Edit Study Case   ///////////////////////
		
		scope.vm.isEdit     = false;
		scope.vm.editCase   = undefined;
		scope.vm.enableEdit = function (__case) {
			scope.vm.initial = !__case ? true: false;
			scope.vm.isEdit = !__case ? false: true;
			scope.vm.editCase = !__case ? undefined : __case;
		};
		
		/////////////////////////   Add new Layer   ///////////////////////
		scope.vm.addNewLayer = undefined;
		scope.vm.dataGeom    = undefined;
		scope.vm.polygonType = undefined;
		scope.vm.postURL     = undefined;
		scope.vm.caseSlug    = undefined;
		
		scope.vm.activateAddNewLayer = function (caseSlug) {
			scope.vm.caseSlug = caseSlug;
			scope.vm.addNewLayer   = true;
			scope.vm.caseSelected  = undefined;
		};

		scope.$watch('vm.dataGeom', changePostUrl, true);
		scope.$watch('vm.indicatorsColsMap', changePostUrlIndicators, true);
		scope.$watch('vm.polygonType', changePostUrlPolygons, true);

		function changePostUrl () {
			if (scope.vm.dataGeom === 'point') {
				scope.vm.postURL = '/api/cases/addpntlyr/';
			} else if (scope.vm.dataGeom === 'polygon') {
				scope.vm.postURL = undefined;
			} else {
				scope.vm.postURL = undefined;
			}
		}

		function changePostUrlIndicators () {
			if (scope.vm.indicatorsColsMap === 'sim') {
				scope.vm.postURL = '/api/cases/addinddata/';
			} else {
				scope.vm.postURL = '/api/cases/addindsdata/';
			}
		}

		function changePostUrlPolygons () {
			if (scope.vm.polygonType === 'polygon-data') {
				scope.vm.postURL = '/api/cases/addpolylyr/';
			}
		}
	};
};


manageStudyCasesController.$inject = ['$scope'];

function manageStudyCasesController($scope) {
	/* jshint validthis: true */
	var vm = this;
};

})();