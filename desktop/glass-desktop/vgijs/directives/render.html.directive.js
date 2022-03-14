(function () {"use strict";


angular
	.module('vgijs.directives')
	.directive('vgijsTextToHtml', textToHtml);

textToHtml.$inject = ['$compile'];

function textToHtml($compile) {
	var directive = {
		restrict   : 'EA',
		scope      : {
			htmltemplate : '='
		},
		link       : link,
		controller : renderHtmlController,
		controllerAs : 'vm',
		bindToController : true
	};
	
	return directive;
	
	function link(scope, iElement, iAttrs) {
		iElement.html('').append(
			$compile(scope.vm.htmltemplate)(scope)
		);
	};
};

renderHtmlController.$inject = ['$scope'];

function renderHtmlController($scope) {
	/* jshint valid this: true */
	var vm = this;
};

})();