(function () {"use strict";

angular
	.module('vgijs.directives')
	.directive('osmToLulcInputs', osmLulc);

osmLulc.$inject = [];

function osmLulc() {
	var directive = {
		restrict : 'E',
		replace  : false,
		transclude : true,
		templateUrl : '/static/vgi-angular/osm-to-lulc-form.html',
		scope : {
			servname     : '=',
			nomenclature : '=',
			drawedit     : '=',
			drawout      : '=',
			drawdel      : '=',
			warnmess     : '=',
			runing       : '='
		},
		link : link,
		controller : osmLulcController,
		controllerAs : 'vm',
		bindToController : true
	};
	
	return directive;
	
	function link(scope, iElement, iAttrs) {
		// Active Draw Rectangle function
		scope.vm.activeDrawBBox = function () {
			scope.vm.drawedit = true;
		};
		
		// User must Draw a rectangle
		scope.vm.pleaseDraw = function () {
			scope.vm.warnmess = '<h3>Interest Area is not defined!</h3>' +
				'<p>Please select an Interest Area and try again</p>';
		};
		
		// Manage Nomenclature Selection
		scope.vm.Nomenclatures = [
			{ name : "URBAN_ATLAS"      , label : "Urban Atlas"      , select : false },
			{ name : "CORINE_LAND_COVER", label : "Corine Land Cover", select : false },
			{ name : "GLOBE_LAND_30"    , label : "Globe Land 30"    , select : false }
		];
		
		scope.vm.selectingNomenclature = function (src) {
			if (!src.select){
				scope.vm.nomenclature = '';
			} else {
				scope.vm.nomenclature = src.name;
				
				scope.vm.Nomenclatures.forEach(function (d) {
					if (d.name !== src.name && d.select) {
						d.select = false;
					}
				});
			}
		};
		
		// User must select Nomenclature
		scope.vm.pleaseSelectNom = function () {
			scope.vm.warnmess = '<h3>LULC Nomenclature is not defined!</h3>' +
				'<p>Please select one LULC Nomenclature and try again.</p>'
		};
		
		// Submit form
		scope.vm.submitForm = function () {
			if (scope.vm.servname == 'osm2lulc_f') {
				scope.vm.runing = '<p>We are downloading the OSM data ' + 
					'avaiable for the selected area.' +
					'This will take a while!</p>';
			} else {
				scope.vm.runing = '<p>We are generating your LULC Map. ' +
					'This will take a while!</p>';
			};
			
			var sb = angular.element(
				document.querySelector('#submitform'));
			
			sb.click();
		};
	};
};

osmLulcController.$inject = ['$scope'];

function osmLulcController($scope) {
	var vm = this;
};

})();