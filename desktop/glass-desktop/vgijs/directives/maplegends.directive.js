(function () {"use strict";

angular
    .module('vgijs.directives')
    .directive('vgijsMapLegend', legend);

legend.$inject = ['$compile'];

function legend($compile) {
    var directive = {
        restrict: 'EA',
        link: link
    };
    
    return directive;
    
    function link(scope, iElement, iAttrs) {
        var legends_info = {
            'URBAN_ATLAS' : [
                {cls: "Urban Fabric", color: "#e6004d"},
                {cls: "Industrial, commercial, public, military, private, and transport units", color: "#cc4df2"},
                {cls: "Mine, dump and construction sites", color: "#986b58"},
                {cls: "Artifical non-agricutural vegetated areas", color: "#a7bd39"},
                {cls: "Agricultural, semi-natural areas, wetlands", color: "#fff9ba"},
                {cls: "Forests", color: "#016f45"},
                {cls: "Water", color: "#b9e5fa"},
                {cls: "NoData", color: "#d3d3d3"}
            ],
            'CORINE_LAND_COVER': [
                {cls: "Urban Fabric", color: "#e6004d"},
                {cls: "Industrial, commercial, public, military, private, and transport units", color: "#cc4df2"},
                {cls: "Mine, dump and construction sites", color: "#986b58"},
                {cls: "Artifical non-agricutural vegetated areas", color: "#a7bd39"},
                {cls: "Agricultural areas", color: "#fff9ba"},
                {cls: "Arable Land", color: "#ffff00"},
                {cls: "Permanent crops", color: "#e68000"},
                {cls: "Pastures", color: "#E6E64D"},
                {cls: "Heterogeneous", color: "#e6cc4d"},
                {cls: "Forests", color: "#016f45"},
                {cls: "Scrub and/or herbaceous vegetation associations", color: "#a6f200"},
                {cls: "Open spaces with little or no vegetation", color: "#e6e6e6"},
                {cls: "Wetlands", color: "#4d4dff"},
                {cls: "Water", color: "#b9e5fa"},
                {cls: "NoData", color: "#d3d3d3"}
            ],
            'GLOBE_LAND_30': [
                {cls: "Cultivated land", color: "#fff9ba"},
                {cls: "Forest", color: "#016f45"},
                {cls: "Grassland", color: "#70a800"},
                {cls: "Scrubland", color: "#e69900"},
                {cls: "Wetland", color: "#02fdc7"},
                {cls: "Water bodies", color: "#00a8e6"},
                {cls: "Tundra", color: "#646432"},
                {cls: "Artificial surfaces", color: "#fe0000"},
                {cls: "Bareland", color: "#cacaca"},
                {cls: "Permanent snow/ice", color: "#d3edfb"},
                {cls: "NoData", color: "#d3d3d3"}
            ]
        };
        
        var array = legends_info[iAttrs.legendClasses];
        var i;
        var template = '<div id="osm-legend">';
        for (i=0; i < array.length; i++) {
            template += '<i style="background:' +
                array[i].color + '; color:' +
                array[i].color + 
                '">class</i> ' + array[i].cls +
                '<br>';
        }
        
        template += '</div>';
        
        iElement.html('').append($compile(template)(scope));
    }
}


})();