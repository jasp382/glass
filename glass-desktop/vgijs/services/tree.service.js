(function () {'use strict';

angular
    .module('vgijs.tree')
    .service('TreeDataGenerator', TreeDataGenerator);

function TreeDataGenerator() {
    var service = {
        getTree: getTree
    };
    
    return service;
    
    ///////////////////////////
    
    function getTree(toolsArray) {
        var tree_array = getRootNodes(toolsArray, 0);
        
        getChildrenNodes(toolsArray, tree_array);
        
        return tree_array;
        
        // Get root nodes
        function getRootNodes(data, root_id) {
            var root_array = [];
            
            data.forEach(function(d) {
                if (d.fields.parent_id === root_id) {
                    root_array.push({
                        'id'    : d.pk,
                        'title' : d.fields.name,
                        'open'  : false
                    });
                }
            });
            
            return root_array;
        }
        
        // Get children nodes
        function getChildrenNodes(data, root) {
            root.forEach(function(d) {
                // flow throw data
                data.forEach(function(e) {
                    if (e.fields.parent_id === d.id) {
                        if (d.nodes) {
                            d.nodes.push({
                                'id'    : e.pk,
                                'title' : e.fields.name,
                                'open'  : false
                            });
                        } else {
                            d['nodes'] = [{
                                'id'    : e.pk,
                                'title' : e.fields.name,
                                'open'  : false
                            }];
                        }
                        // Do it for all existent sub-children
                        getChildrenNodes(data, d.nodes);
                    }
                });
            });
        }
    }
}

})();