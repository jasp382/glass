(function () {'use strict';

angular
    .module('vgijs.controllers')
    .controller('CreditsController', CreditsController);

CreditsController.$inject = [
    '$scope', '$window', 'deviceDetector'
];

function CreditsController($scope, $window, deviceDetector) {
    var mapVm = this;
    
    mapVm.browser = deviceDetector.browser;
    
    if (mapVm.browser !== 'chrome') {
    	$window.location.href = '/expvgi/?browser=1'
    };
}

})();