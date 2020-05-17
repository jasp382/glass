(function () {'use strict';

/* Factories for VGI Search Web Service */
angular
	.module('vgijs.api')
	.factory('ViewLayers', ViewLayers);

angular
	.module('vgijs.api')
	.factory('ListLyrOsmToLulc', ListLyrOsmToLulc);

angular
	.module('vgijs.api')
	.factory('ListLyrDsn', ListLyrDsn);

ViewLayers.$inject       = ['$resource', 'API_URL'];
ListLyrOsmToLulc.$inject = ['$resource', 'API_URL'];
ListLyrDsn.$inject       = ['$resource', 'API_URL'];

function ViewLayers($resource, API_URL) {
	return $resource(
		API_URL + '/api/cpu/db/json/cpu_layers/:id',
		{id: '@id'}
	)
}

function ListLyrOsmToLulc($resource, API_URL) {
	return $resource(
		API_URL + '/api/rest/osmtolulc/rqsts/:id', {id : '@id'}
	)
}

function ListLyrDsn($resource, API_URL) {
	return $resource(
		API_URL + '/api/rest/dsn/rqsts/:id', {id : '@id'}
	)
}

})();