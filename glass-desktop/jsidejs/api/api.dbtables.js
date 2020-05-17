(function () {'use strict';

/* Factories to jside_db API */

angular
	.module('jsidejs.api')
	.factory('Indicators', Indicators);

angular
	.module('jsidejs.api')
	.factory('YearsTable', YearsTable);

angular
	.module('jsidejs.api')
	.factory('YearsLyrTbl', YearsLyrTbl);

angular
	.module('jsidejs.api')
	.factory('GrpStatsTable', GrpStatsTable);

angular
	.module('jsidejs.api')
	.factory('StudyCases', StudyCases);

angular
	.module('jsidejs.api')
	.factory('GetDataset', GetDataset);

angular
	.module('jsidejs.api')
	.factory('GetDatasetCols', GetDatasetCols);

angular
	.module('jsidejs.api')
	.factory('LayersTbl', LayersTbl);

angular
	.module('jsidejs.api')
	.factory('PntLyrTbl', PntLyrTbl);

angular
	.module('jsidejs.api')
	.factory('PolyLyrTbl', PolyLyrTbl);

angular
	.module('jsidejs.api')
	.factory('Settings', Settings);

Indicators.$inject     = ['$resource'];
YearsTable.$inject     = ['$resource'];
YearsLyrTbl.$inject    = ['$resource'];
GrpStatsTable.$inject  = ['$resource'];
Settings.$inject       = ['$resource'];
StudyCases.$inject     = ['$resource'];
GetDataset.$inject     = ['$resource'];
GetDatasetCols.$inject = ['$resource'];
LayersTbl.$inject      = ['$resource'];
PntLyrTbl.$inject      = ['$resource'];
PolyLyrTbl.$inject     = ['$resource'];

function Indicators($resource) {
	return $resource('/api/tlyr/lst-theme-lyr/:id', {id : '@id'});
}

function YearsTable($resource) {
	return $resource('/api/years/list/:id', {id : '@id'});
}

function YearsLyrTbl($resource) {
	return $resource('/api/cases/indicatorsbyear/:id', {id : '@id'});
}

function GrpStatsTable($resource) {
	return $resource('/api/su/lstsu/:id', {id : '@id'});
}

function StudyCases($resource) {
	return $resource('/api/cases/lstcases/:id', {id : '@id'});
}

function GetDataset($resource) {
	return $resource('/api/datasets/table/:id', {id : '@id'});
}

function GetDatasetCols($resource) {
	return $resource('/api/rest/datasets/cols/:id', {id : '@id'});
}

function LayersTbl($resource) {
	return $resource('/api/cases/indicators/:id', {id : '@id'});
}


function Settings($resource) {
	return $resource('/api/geoserver/:id', {id : '@id'});
}

function PntLyrTbl($resource) {
	return $resource('/api/cases/lstpntlyr/:id', {id : '@id'});
}

function PolyLyrTbl($resource) {
	return $resource('/api/cases/lstpolylyr/:id', {id : '@id'});
}

})();