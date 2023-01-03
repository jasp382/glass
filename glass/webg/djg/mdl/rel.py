"""
Get relations between django models
"""

from glass.pys import __import


def order_mdl_by_rel(mdl_cls):
    """
    Receive a group of tables and see which tables should be
    imported first in the database. Tables depending on others should be
    imported after them.
    """
    
    import os
    from glass.webg.djg.mdl.i    import lst_mdl_no_fk
    from django.contrib.gis.db import models
    
    def get_childs(tree_obj):
        for mdl in tree_obj:
            mdl_cls = __import(mdl)
            
            rel_model_name = None
            rel_app_name   = None
        
            fields = mdl_cls._meta.get_fields()
        
            for field in fields:
                if not isinstance(field, models.ForeignKey):
                    if hasattr(field, 'related_model'):
                        if hasattr(field.related_model, '__name__'):
                            rel_model_name = field.related_model.__name__
                            rel_app_name   = field.related_model.__module__.split('.')[0]
                        else:
                            rel_model_name = None
                            rel_app_name = None
                    else:
                        rel_model_name = None
                        rel_app_name = None
                else:
                    rel_model_name = None
                    rel_app_name = None
        
                if rel_model_name and rel_app_name:
                    rmn = '{}.models.{}'.format(rel_app_name, rel_model_name)
                    
                    tree_obj[mdl].update({rmn: {}})
        
                else: 
                    continue
            
            if tree_obj[mdl]:
                get_childs(tree_obj[mdl])
            
            else: continue
    
    
    def get_mdl_level(nodes, level, dic):
        for node in nodes:
            if level not in dic:
                dic[level] = [node]
            else:
                dic[level].append(node)
            
            if not nodes[node]:
                continue
            else:
                get_mdl_level(nodes[node], level + 1, dic)
    
    # Get root
    root_tables = lst_mdl_no_fk(mdl_cls)
    tree = {root : {} for root in root_tables}
    
    get_childs(tree)
    
    mdl_by_level = {}
    get_mdl_level(tree, 0, mdl_by_level)
    
    # Levels to a single list
    ordened = []
    for i in range(len(mdl_by_level.keys())):
        for mdl in mdl_by_level[i]:
            ordened.append(mdl)
    
    clean = []
    for i in range(len(ordened)):
        if i+1 != len(ordened):
            if ordened[i] not in ordened[i+1:]:
                clean.append(ordened[i])
            else: continue
        else:
            if ordened[i] not in clean:
                clean.append(ordened[i])
    
    return clean

