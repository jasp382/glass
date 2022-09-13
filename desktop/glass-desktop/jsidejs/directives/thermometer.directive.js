(function () {'use strict';

angular
    .module('jsidejs.directives')
    .directive('jsideThermometer', thermometer);

thermometer.$inject = ['d3'];

function thermometer(d3) {
	var directive = {
		replace : false,
		restrict : 'E',
		scope : {
			width   : '=',
			minval  : '=',
			maxval  : '=',
			meanval : '=',
			rowval  : '=',
			color   : '='
		},
		link: link,
		controller : ThermometerController,
		controllerAs: 'vm',
		bindToController: true
	};
	
	return directive;
	
	function link(scope, element, attrs) {
		var padding = {
				left : parseInt(attrs.padding, 10),
				right: parseInt(attrs.padding, 10)
			},
			margin = {
				top    : parseInt(attrs.margin, 10),
				bottom : parseInt(attrs.margin, 10),
				right  : 0,
				left   : 0
			},
			width = scope.vm.width - padding.left - padding.right,
			height = parseInt(attrs.height, 10) - margin.top - margin.bottom,
			labelHeight = 12,
			dontAnimate = attrs.hasOwnProperty('dontAnimate') && attrs.dontAnimate.toLowerCase() !== 'false',
			x = d3.scaleLinear().range([0, width]),
			y = d3.scaleBand().domain(1).rangeRound([0, height]);
		
		var chart = d3.select(element[0])
			.append('svg')
				.attr('width', width + padding.left + padding.right)
				.attr('height', height + margin.top + margin.bottom + labelHeight)
			.append('g')
				.attr('transform', 'translate(' + padding.left + ',' + margin.top + ')');
		
		var referenceLine = d3.line();
		
		var minval  = parseInt(scope.vm.minval),
			maxval  = parseInt(scope.vm.maxval),
			meanval = parseInt(scope.vm.meanval),
			realval = parseInt(scope.vm.rowval);
		
		/*AXES */
		x.domain([minval, maxval]);
		chart.append('g')
			.attr('class', 'x axis')
			.attr('transform', 'translate(0,' + height + ')')
			.call(d3.axisBottom(x).ticks(0));
		
		chart.append('text')
			.attr('class', 'axis zero')
			.attr('x', x(minval))
			.attr('y', height + labelHeight)
			.attr('dy', 5)
			.attr('dx', -2)
			.attr('text-anchor', 'left')
			.text(minval);
		
		chart.append('text')
			.attr('class', 'axis max')
			.attr('x', x(maxval))
			.attr('y', height + labelHeight)
            .attr('dy', 5)
            .attr('dx', 3)
            .attr('text-anchor', 'end')
            .text(maxval);
		
		// NOTE: The order of the chart elements is important!
		// Background
		chart.append('rect')
            .attr('class', 'background')
            .attr('x', 0)
            .attr('y', 0)
            .attr('height', height)
            .attr('width', width);
		
		// Value
        chart.append('rect')
            .attr('class', 'bar value')
            .attr('style', 'fill: ' + scope.vm.color)
            .attr('x', x(minval))
            .attr('y', 0)
            .attr('height', height)
            .attr('width', x(realval));
		
		chart.append('path')
			.attr('class', 'line ref')
			.attr('d', referenceLine([
				[x(meanval), 0], [x(meanval), height]
			]));
		
		// WATCHERS
		scope.$watch(
			'[vm.minval, vm.maxval, vm.meanval, vm.rowval]',
			updateChart, true
		);
		
		function updateChart () {
			var minval  = parseInt(scope.vm.minval),
				maxval  = parseInt(scope.vm.maxval),
				meanval = parseInt(scope.vm.meanval),
				realval = parseInt(scope.vm.rowval);
			
			x.domain([0, maxval]);
			
			//chart.select('.axis.max')
				//.attr('x', x(maxval))
				//.text(d3.format(maxFormat)(maxval));
			
			chart.selectAll('.bar.value')
                .attr('style', 'fill: ' + scope.vm.color)
                .transition()
                    .duration(1000)
                .attr('width', x(realval));
			
			chart.select('.line.ref')
                .transition()
                    .duration(700)
                .attr('d', referenceLine([
					[x(meanval), 0], [x(meanval), height]
				]));
		};
	};
};

ThermometerController.$inject = [
    '$scope'
];

function ThermometerController($scope) {
    /* jshint validthis: true */
    var vm = this;
};

})();