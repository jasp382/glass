(function () {'use strict';

angular
    .module('jsidejs', [
        /* Dependencies */
        /* Angular modules */
        'ngRoute',
        'ngSanitize',
        /* Feature modules */
        'jsidejs.directives',
		'jsidejs.components',
        //'jsidejs.controllers',
        'jsidejs.services',
        /* Constants module */
        'jsidejs.constants',
        /* API module */
        'jsidejs.api'
    ]);

})();