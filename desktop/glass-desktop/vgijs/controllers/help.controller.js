(function () {'use strict';

angular
    .module('vgijs.controllers')
    .controller('HelpController', HelpController);

HelpController.$inject = [
    '$scope', '$window', 'deviceDetector'
];

function HelpController($scope, $window, deviceDetector) {
    var mapVm = this;
    
    mapVm.browser = deviceDetector.browser;
    
    if (mapVm.browser !== 'chrome') {
    	$window.location.href = '/expvgi/?browser=1'
    };
}

})();