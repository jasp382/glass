(function () {'use strict';


/* Factories for GeoTimeLine Web Services */

angular
	.module('vgijs.api')
	.factory('FireEvents', FireEvents);

FireEvents.$inject = ['$resource', 'API_URL'];

function FireEvents($resource, API_URL) {
	return $resource(
		API_URL + '/api/geotimeline/events/:id', {id : '@id'}
	)
}

})();