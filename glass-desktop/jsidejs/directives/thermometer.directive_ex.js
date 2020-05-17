(function () {'use strict';

/**
 * @desc Thermometer directive to build thermometer charts
 * @example <eurohealthy-thermometer
 *              value="787"
 *              max="890"
 *              class-level="6"
 *              colors="vm.colors">
 *          </eurohealthy-thermometer>
 */
angular
    .module('jsidejs.directives')
    .directive('jsideThermometer', thermometer);

thermometer.$inject = [
    'd3',
    'ChartUtils',
    'colorService',
    'MODEL_DEFAULT_MAX',
    'MODEL_DEFAULT_MIN'
];

function thermometer(d3,
                     ChartUtils,
                     colorService,
                     MODEL_DEFAULT_MAX,
                     MODEL_DEFAULT_MIN) {
    var directive = {
        replace: false,
        restrict: 'E',
        scope: {
            colors    : '=',
            classLevel: '=',
            value     : '=',
            max       : '=?',
            ref       : '=?',
            width     : '=?'
        },
        link: link,
        controller: ThermometerController,
        controllerAs: 'vm',
        bindToController: true
    };

    return directive;


    function DataHandler(value, classLevel, max, ref, height) {
        return {
            value     : isNaN(value)      ? MODEL_DEFAULT_MIN : value,
            classLevel: isNaN(classLevel) ? 0 : classLevel,
            max       : isNaN(max)        ? MODEL_DEFAULT_MAX : max,
            ref       : isNaN(ref)        ? undefined : ref,
            height    : height,
            update    : function (v, c, m, r) {
                this.value      = isNaN(v) ? MODEL_DEFAULT_MIN : v;
                this.classLevel = isNaN(c) ? 0 : c;
                this.max        = isNaN(m) ? MODEL_DEFAULT_MAX : m;
                this.ref        = isNaN(r) ? undefined : r;
            },
            getReference: function (x) {
                if (angular.isUndefined(this.ref)) return [];
                return [
                    [x(this.ref),      0],
                    [x(this.ref), this.height]
                ];
            }
        };
    }


    function link(scope, element, attrs) {
        // Check defaults
        var padding = {
                left : parseInt(attrs.padding, 10),
                right: parseInt(attrs.padding, 10)
            },
            margin = {
                top   : parseInt(attrs.margin, 10),
                bottom: parseInt(attrs.margin, 10),
                right : 0,
                left  : 0
            },
            width       = scope.vm.width - padding.left - padding.right,
            height      = parseInt(attrs.height, 10) - margin.top - margin.bottom,
            labelHeight = 12,
            // TODO: Animations
            dontAnimate = attrs.hasOwnProperty('dontAnimate') && attrs.dontAnimate.toLowerCase() !== 'false',
            x = d3.scaleLinear().range([0, width]),
            y = d3.scaleBand().domain(1).rangeRound([0, height]);

        colorService.updateColors(scope.vm.colors);

        // Group data in a single object
        var dataHandler = new DataHandler(
            scope.vm.value,
            scope.vm.classLevel,
            scope.vm.max,
            scope.vm.ref,
            height
        );

        var chart = d3.select(element[0])
            .append('svg')
                .attr('width', width + padding.left + padding.right)
                .attr('height', height + margin.top + margin.bottom + labelHeight)
            .append('g')
                .attr('transform', 'translate(' + padding.left + ',' + margin.top + ')');

        var referenceLine = d3.line();

        /*
         * AXES
         */
        x.domain([MODEL_DEFAULT_MIN, MODEL_DEFAULT_MAX]);
        chart.append('g')
            .attr('class', 'x axis')
            .attr('transform', 'translate(0,' + height + ')')
            .call(d3.axisBottom(x).ticks(0));

        chart.append('text')
            .attr('class', 'axis zero')
            .attr('x', x(MODEL_DEFAULT_MIN))
            .attr('y', height + labelHeight)
            .attr('dy', 5)
            .attr('dx', -2)
            .attr('text-anchor', 'left')
            .text(MODEL_DEFAULT_MIN);

        chart.append('text')
            .attr('class', 'axis max')
            .attr('x', x(MODEL_DEFAULT_MAX))
            .attr('y', height + labelHeight)
            .attr('dy', 5)
            .attr('dx', 3)
            .attr('text-anchor', 'end')
            .text(MODEL_DEFAULT_MAX);

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
            .attr('style', 'fill: ' + colorService.getColor(dataHandler.classLevel))
            .attr('x', x(0))
            .attr('y', 0)
            .attr('height', height)
            .attr('width', x(dataHandler.value));

        chart.append('path')
            .attr('class', 'line ref')
            .attr('d', referenceLine(dataHandler.getReference(x)));

        // WATCHERS
        scope.$watch('[vm.value, vm.classLevel, vm.max, vm.ref]', updateData, true);
        scope.$watch('vm.width', updateChartWidth);

        function updateChartWidth(newWidth) {
            width = newWidth - padding.left - padding.right;

            d3.select(element[0])
                .select('svg')
                    .attr('width', width + padding.left + padding.right)

            x = d3.scaleLinear().range([0, width]);
            x.domain([0, dataHandler.max]);

            chart.select('.background')
                .attr('width', width);
            chart.select('.bar.value')
                .attr('width', x(dataHandler.value));
            chart.select('.line.ref')
                .attr('d', referenceLine(dataHandler.getReference(x)));

            var maxFormat = ChartUtils.guessFormatting(x.domain());
            chart.select('.axis.max')
                .attr('x', x(dataHandler.max))
                .text(d3.format(maxFormat)(dataHandler.max));
        }

        function updateData(newData) {
            dataHandler.update(
                newData[0],
                newData[1],
                newData[2],
                newData[3]
            );

            x.domain([0, dataHandler.max]);
            var maxFormat = ChartUtils.guessFormatting(x.domain());
            chart.select('.axis.max')
                .attr('x', x(dataHandler.max))
                .text(d3.format(maxFormat)(dataHandler.max));

            chart.selectAll('.bar.value')
                .attr('style', 'fill: ' + colorService.getColor(dataHandler.classLevel))
                .transition()
                    .duration(1000)
                .attr('width', x(dataHandler.value));

            // TODO: Sometimes we might not want animations

            chart.select('.line.ref')
                .transition()
                    .duration(700)
                .attr('d', referenceLine(dataHandler.getReference(x)));
        }
    }
}


ThermometerController.$inject = [
    '$scope'
];

function ThermometerController($scope) {
    /* jshint validthis: true */
    var vm = this;
}

})();
