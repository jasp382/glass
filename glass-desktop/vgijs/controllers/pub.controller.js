(function () {'use strict';

angular
    .module('vgijs.controllers')
    .controller('PublicationsController', PublicationsController);

PublicationsController.$inject = [
    '$scope', '$window', 'deviceDetector'
];

function PublicationsController($scope, $window, deviceDetector) {
    var mapVm = this;
    
    mapVm.browser = deviceDetector.browser;
    
    if (mapVm.browser !== 'chrome') {
    	$window.location.href = '/expvgi/?browser=1'
    };
}

})();