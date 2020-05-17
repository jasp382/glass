(function () {'use strict';

angular
	.module('vgijs.charts')
	.directive('timeLineChart', timeLineChart);

timeLineChart.$inject = ['d3'];

function timeLineChart(d3) {
	var directive = {
		replace : false,
		restrict : 'E',
		scope : {
			selevents  : '=',
			selcontrib : '='
		},
		link : link,
		controller : timeLineChartController,
		controllerAs: 'vm',
		bindToController : true
	};

	return directive;

	function link(scope, element, attrs) {
		var values = scope.vm.selevents.contrib;

		var margin = {top: 10, right: 30, bottom: 30, left: 50},
			width  = 700 - margin.left - margin.right,
			height = 100 - margin.top - margin.bottom;
		
		// Add an SVG element with the desired dimensions and margin.
		var svg = d3.select(element[0])
			.append("svg")
				.attr("width", width + margin.left + margin.right)
				.attr("height", height + margin.top + margin.bottom)
			.append("g")
				.attr("transform",
				"translate(" + margin.left + "," + margin.top + ")");
		
		// Time String to Time Value
		values.forEach(function (d) {
			d.ctime = d3.timeParse("%Y-%m-%d %H:%M:%S")(d.ctime);
			d.event = parseInt(d.event);
		});

		// Add X axis --> it is a date format
		var x = d3.scaleTime()
			.domain(d3.extent(values, function(d) { return d.ctime; }))
			.range([ 0, width ]);
		svg.append("g")
			.attr("transform", "translate(0," + (height+5) + ")")
			.call(d3.axisBottom(x).ticks(10).tickSizeOuter(0));
		
		// Add Y axis
		var y = d3.scaleLinear()
			//.domain( d3.extent(values, function(d) { return +d.event; }) )
			.domain([0, 2]).nice()
			.range([height, 0]);
		svg.append("g")
			.attr("transform", "translate(-5,0)")
			.call(d3.axisLeft(y).ticks(0).tickSizeOuter(0));
		
		// Add the area
		/*
		svg.append("path")
			.datum(values)
			.attr("fill", "#69b3a2")
			.attr("fill-opacity", .3)
			.attr("stroke", "none")
			.attr("d", d3.area()
				.x(function(d) { return x(d.ctime) })
				.y0( height )
				.y1(function(d) { return y(d.event) })
			)*/
		
		// Add the line
		svg.append("path")
			.datum(values)
			.attr("fill", "none")
			.attr("stroke", "#000000")
			.attr("stroke-width", 2)
			.attr("d", d3.line()
				.x(function(d) { return x(d.ctime) })
				.y(function(d) { return y(d.event) })
			)
		
		// Add the line
		svg.selectAll("myCircles")
			.data(values)
			.enter()
			.append("circle")
				.attr("fill", "red")
				.attr("stroke", "none")
				.attr("cx", function(d) { return x(d.ctime) })
				.attr("cy", function(d) { return y(d.event) })
				.attr("r", 6)
				.on("click", clickAction)
				.on("mouseover", handleMouseOver)
				.on("mouseout", handleMouseOut);
		
		function handleMouseOver(d, i) {
			// Use D3 to select element, change color and size
			d3.select(this)
				.attr("fill", "orange")
				.attr("r", 10);

			// Specify where to put label of text
			/*
			svg.append("text")
				.attr("id", "p_" + d.fid.toString())
				.attr("x", function() { return x(d.ctime); })
				.attr("y", function() { return y(d.event+2); })
			.text(function () {
				return d.fb[0].page_ref + ' ' + d.fb[0].datahora;  // Value of the text
			});*/
		};

		function handleMouseOut (d, i) {
			// Use D3 to select element, change color back to normal
			d3.select(this)
				.attr("fill", "red")
				.attr("r", 6);

			// Select text by id and then remove
			d3.select("p_" + d.fid.toString()).remove();
		};

		function clickAction (d, i) {
			scope.$apply(function () {
				scope.vm.selcontrib = d;
			});
		};

		/*
		// Scales and axes. Note the inverted domain for the y-scale: bigger is up!
		var x = d3.time.scale().range([0, width]),
			y = d3.scale.linear().range([height, 0]),
			xAxis = d3.svg.axis().scale(x).tickSize(-height).tickSubdivide(true)
				.tickFormat(d3.time.format("%Y-%m-%d %H:%M:%S")),
			yAxis = d3.svg.axis().scale(y).ticks(4).orient("left");
		
		// An area generator, for the light fill.
		var area = d3.svg.area()
			.interpolate("monotone")
			.x(function(d) { return x(d.ctime); })
			.y0(height)
			.y1(function(d) { return y(d.event); });
		
		var line = d3.svg.line()
			.interpolate("monotone")
			.x(function(d) { return x(d.ctime); })
			.y(function(d) { return y(d.event); })
		
		// Compute the minimum and maximum date, and the maximum event.
		x.domain([values[0].ctime, values[values.length -1].ctime]);
		y.domain([0, 10]).nice();
		
		// Add the clip path.
		svg.append("clipPath")
			.attr("id", "clip")
			.append("rect")
				.attr("width", width)
				.attr("height", height);
		
		// Add the x-axis.
		svg.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + height + ")")
			.call(xAxis)
			.selectAll("text")
				.style("text-anchor", "end")
				.attr("dx", "-.8em")
				.attr("dy", ".15em")
				.attr("transform", "rotate(-45)");
		
		// Add the y-axis.
		svg.append("g")
			.attr("class", "y axis")
			.attr("transform", "translate(" + width + ",0)")
			.call(yAxis);
		
		var stroke_color = '#002bff',
			colors = d3.scale.category10();
		svg.selectAll('.line')
			//.data([values, msft, ibm])
			.data([values])
			.enter()
				.append('path')
				.attr('class', 'line')
				.style('stroke', stroke_color)
				.attr('clip-path', 'url(#clip)')
				.attr('d', function(d) {
					return line(d);
				});
		*/
		
		/* Add 'curtain' rectangle to hide entire graph */
		/*
		var curtain = svg.append('rect')
			.attr('x', -1 * width)
			.attr('y', -1 * height)
			.attr('height', height)
			.attr('width', width)
			.attr('class', 'curtain')
			.attr('transform', 'rotate(180)')
			.style('fill', '#ffffff');
		*/
		/* Optionally add a guideline */
		/*
		var guideline = svg.append('line')
			.attr('stroke', '#333')
			.attr('stroke-width', 0)
			.attr('class', 'guide')
			.attr('x1', 1)
			.attr('y1', 1)
			.attr('x2', 1)
			.attr('y2', height);*/
		
		/* Create a shared transition for anything we're animating */
		/*var t = svg.transition()
			.delay(750)
			.duration(80000)
			.ease('linear')
			.each('end', function() {
				d3.select('line.guide')
					.transition()
					.style('opacity', 0)
					.remove()
			});
			
		t.select('rect.curtain')
			.attr('width', 0)
		t.select('line.guide')
			.attr('transform', 'translate(' + width + ', 0)');
			
		d3.select("#show_guideline").on("change", function(e) {
			guideline.attr('stroke-width', this.checked ? 1 : 0);
			curtain.attr("opacity", this.checked ? 0.75 : 1);
		});*/
	};
};

timeLineChartController.$inject = ['$scope'];

function timeLineChartController($scope) {
	/* jshint validthis: true */
	var vm = this;
};

})();