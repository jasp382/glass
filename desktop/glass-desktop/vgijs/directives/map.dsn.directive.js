(function () {"use strict";

angular
	.module('vgijs.directives')
	.directive('vgijsMapDsn', dsnMapping);


dsnMapping.$inject = [];


function dsnMapping() {
	var directive = {
		restrict         : 'E',
		replace          : false,
		transclude       : true,
		templateUrl      : '/static/vgi-angular/dsn-map-form.html',
		scope            : {
			drawedit   : '=',
			drawout    : '=',
			drawradius : '=',
			drawdel    : '=',
			keyword    : '=',
			datasrc    : '=',
			warnmess   : '=',
			runing     : '='
		},
		link             : link,
		controller       : dsnMappingController,
		controllerAs     : 'vm',
		bindToController : true
	};
	
	return directive;
	
	function link(scope, iElement, iAttrs) {
		// Manage datasources where we will search for data
		scope.vm.dataSources = [
	        {
	            name : 'FACEBOOK', radius : 'no_restritions', 'select' : false,
	            warning: '<p>Facebook option is temporarilly unavailable</p>',
				label: 'Facebook'
	        },
	        {
	            name : 'TWITTER' , radius : 3000,  'select' : false,
	            warning: '<p>Twitter allows a radius minor or equal a 3km!</p>',
	            label: 'Twitter'
	        },
	        {
	            name : 'FLICKR'  , radius : 32000, 'select' : false,
	            warning: '<p>Flickr allows a radius minor or equal a 32km!</p>',
	            label: 'Flickr'
	        },
	        {
	            name : 'YOUTUBE' , radius : 'no_restritions', 'select' : false,
	            warning: 'Youtube Warning', label: 'Youtube'
	        }
	    ];
		
		scope.vm.selectingDataSources = function (src) {
			if (src.select) {
				if (scope.vm.datasrc === '') {
					scope.vm.datasrc = src.name;
				} else {
					scope.vm.datasrc += ';' + src.name;
				}
			} else {
				if (scope.vm.datasrc.indexOf(';' + src.name) > -1) {
					scope.vm.datasrc = scope.vm.datasrc.replace(';' + src.name, '');
				} else {
					if (scope.vm.datasrc.indexOf(src.name + ';') > -1) {
						scope.vm.datasrc = scope.vm.datasrc.replace(src.name + ';', '');
					} else {
						scope.vm.datasrc = scope.vm.datasrc.replace(src.name, '');
					}
				}
			}
		};
		
		// User must select datasources
		scope.vm.pleaseSelectSomething = false;
		scope.vm.pleaseSelectDataSource = function () {
			scope.vm.warnmess = '<h3>Data Sources definition!</h3>' +
				'<p>You must select some data sources.</p>' +
				'<p>The service will search for data in the selected sources.</p>';
		};
		
		// Active Draw circle function
		scope.vm.activeDrawCircle = function () {
			scope.vm.drawedit = true;
		};
		
		// User must draw a circle
		scope.vm.pleaseDraw = function () {
			scope.vm.warnmess = '<h3>Search radius definition!</h3>' +
				'<p>You must draw your search radius before you go.</p>' +
				'<p>Please use the button "Select Search Area" to do it.</p>';
		};
		
		// Check if radius is consistent with datasources requirements
		scope.$watchCollection(
			'[vm.drawradius, vm.datasrc]', checkRadius, true
		);
		
		scope.$watch('vm.datasrc', faceIsNotAvailable, true);
		
		function checkRadius () {
			if (!scope.vm.drawradius) return;
			
			scope.vm.dataSources.forEach(function(d) {
				if (d.select && d.radius !== 'no_restritions') {
					if (scope.vm.drawradius > d.radius) {
						if (scope.vm.warnmess === '') {
							scope.vm.warnmess = '<h3>Warning! Radius is not according requirements</h3>'+
								d.warning;
						} else {
							scope.vm.warnmess = scope.vm.warnmess + d.warning;
						}
					}
				}
			});
			
			if (scope.vm.warnmess !== '') {
				scope.vm.drawdel = true;
			}
		};
		
		function faceIsNotAvailable () {
			if (scope.vm.datasrc === '') return;
			
			scope.vm.dataSources.forEach(function (d) {
				if (d.name === 'FACEBOOK' && d.select) {
					if (scope.vm.warnmess === '') {
						scope.vm.warnmess = d.warning;
						
						d.select = false;
						
						if (scope.vm.datasrc.indexOf(';FACEBOOK') > -1) {
							scope.vm.datasrc = scope.vm.datasrc.replace(';FACEBOOK', '');
						} else {
							if (scope.vm.datasrc.indexOf('FACEBOOK;') > -1) {
								scop.vm.datasrc = scope.vm.datasrc.replace('FACEBOOK;', '');
							} else {
								scope.vm.datasrc = scope.vm.datasrc.replace('FACEBOOK', '');
							}
						}
						
						return;
					}
				}
			});
		};
		
		// Submit form
		scope.vm.submitForm = function () {
			scope.vm.runing = '<p>We are searching data for you. This will take a while!</p>';
			
			var sb = angular.element(
				document.querySelector('#submitform'));
			
			sb.click();
		};
	};
};

dsnMappingController.$inject = ['$scope'];

function dsnMappingController($scope) {
	/* jshint validthis: true */
	var vm = this;
}

})();