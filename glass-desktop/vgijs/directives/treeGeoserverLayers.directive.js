(function () {'use strict';

angular
	.module('vgijs.directives')
	.directive('geoserverLayersTree', geoserverLayersTree);

geoserverLayersTree.$inject = ['$compile'];

function geoserverLayersTree($compile) {
	var directive = {
		restrict: 'EA',
		link: link
	};

	return directive;

	function link(scope, iElement, iAttrs) {
		var template = 
			'<li ng-repeat="node in ' + iAttrs.treeNodes + '" >' +
				'<span ng-if="node.fields.status"' +
					'class="fa fa-minus" aria-hidden="true"' +
					'style="color: #C0C0C0"' +
					'ng-click="' + iAttrs.treeToogle +'(node)">' +
				'</span>' +
				'<span ng-if="!node.fields.status"' +
					'class="fa fa-plus" aria-hidden="true"' +
					'style="color: #C0C0C0"' +
					'ng-click="' + iAttrs.treeToogle +'(node)">' +
				'</span>' +
				'<a ng-click="' + iAttrs.treeRef +'(node)"' +
					'class="node.fields.css">{{ node.fields.name }}' +
				'</a>' +
				'<ul geoserver-layers-tree ' +
					'tree-nodes="node.fields.child" ' +
					'tree-toogle="' + iAttrs.treeToogle + '" ' + 
					'tree-ref="' + iAttrs.treeRef + '" ' +
					'layer-control="' + iAttrs.layerControl + '" ' +
					'ng-if="!!node.fields.child && node.fields.status" ng-hide="!node.fields.status">' +
				'</ul>' +
				'<ul ng-if="!!node.fields.layers && node.fields.status">' +
					'<li ng-repeat="lyr in node.fields.layers">' +
						'<input type="checkbox" ' +
							'ng-change="' + iAttrs.layerControl + '(lyr)" '+
							'ng-model="lyr.fields.status"><a>{{ lyr.fields.name}}</a>' +
					'</li>' +
				'</ul>' +
			'</li>';

		iElement.html('').append($compile(template)(scope));
	}
}

})();