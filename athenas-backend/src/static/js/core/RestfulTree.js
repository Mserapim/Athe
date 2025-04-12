/**
 *
 **/
Ext._define('core.RestfulTree', {
    'extend': 'Ext.tree.TreePanel',

    'restWindow': undefined,

    'folderIndexField': undefined,

    'factoryRestfulWindow': function(cfg) {
        return Ext._create(this.restWindow, cfg);
    },

    'factoryRestful': function(cfg) {
        var restWnd = this.factoryRestfulWindow({});
        return restWnd.factoryRestful();
    },

    'getLoader': function() {
        if(!this._loader) {
            this._loader = Ext._create('Ext.tree.TreeLoader', {
                'nodeParameter': 'node',
                'url': this.factoryRestful().getRoute('folder').url,
                'requestMethod': 'GET'
            });
        }

        return this._loader;
    },

    'getFolderIndexField': function() {
        return this.folderIndexField;
    },

    'moveItem': function() {
        var selected = this.getSelectionModel().getSelectedNode();

        Ext._create('core.TreeMoveWindow', {
            'restWindow': this.restWindow,
            'folderIndexField': this.folderIndexField,
            'selected': selected,
            'callback': {
                'success': {
                    'scope': this,
                    'fn': function(movedTo) {
                        selected.parentNode.reload();
                    }
                }
            }
        }).show();
    },

    'removerItem': function() {
        var selected = core.nullValue(
            this.getSelectionModel().getSelectedNode(),
            this.getRootNode()
        );
        var rest = this.factoryRestful();

        if(selected.id == this.getRootNode().id)
            Ext.Msg.show({
                'title': 'Removendo',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Selecione primeiro um item.'
            });
        else {
            rest.remove(
                selected.id,
                {
                    'externalCallback': {
                        'success': {
                            'fn': function() {
                                selected.parentNode.reload();
                            }
                        }
                    }
                },
                {
                    'el': this.getEl(),
                    'msg': 'Removendo o item...'
                }
            )
        }

    },

    getParams: function() {
        this._params = core.nullValue(this._params, {});
        return this._params;
    },

    getParam: function(property) {
        return this.getParams()[property];
    },

    setParams: function(params) {
        this._params = params;
    },

    setParam: function(property, value) {
        this.getParams()[property] = value;
    },

    'createItem': function() {
        var params = this.getParams();
        var selected = core.nullValue(
            this.getSelectionModel().getSelectedNode(),
            this.getRootNode()
        );
        var field = this.getFolderIndexField();

        if(selected.id != '0')
            params[field] = selected.id;
        else
            params[field] = null;

        this.factoryRestfulWindow({
            'action': 'create',
            'params': params,
            'callback': {
                'success': {
                    'scope': this,
                    'fn': function() {
                        if(!selected.leaf) selected.reload();
                        else selected.parentNode.reload();
                    }
                }
            }
        }).show();
    },

    'updateItem': function() {
        var params = this.getParams();
        var selected = core.nullValue(
            this.getSelectionModel().getSelectedNode(),
            this.getRootNode()
        );
        var field = this.getFolderIndexField()

        if(selected.id != '0')
            params[field] = selected.parentNode.id;

        if(selected.id == this.getRootNode().id)
            Ext.Msg.show({
                'title': 'Editando',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Selecione primeiro um item.'
            });
        else {
            this.factoryRestfulWindow({
                'action': 'update',
                'values': 'remote',
                'oId': selected.id,
                'params': params,
                'callback': {
                    'success': {
                        'scope': this,
                        'fn': function() {
                            selected.parentNode.reload();
                        }
                    }
                }
            }).show();
        }
    },

    'getToolbar': function() {
        if(!this._toolbar)
            this._toolbar = Ext._create('Ext.Toolbar', {
                'items': [
                    {
                        'text': 'Novo',
                        'iconCls': 'icon-core icon-core-add',
                        'scope': this,
                        'handler': this.createItem
                    },
                    {
                        'text': 'Editar',
                        'iconCls': 'icon-core icon-core-edit',
                        'scope': this,
                        'handler': this.updateItem
                    },
                    {
                        'text': 'Remover',
                        'iconCls': 'icon-core icon-core-delete',
                        'scope': this,
                        'handler': this.removerItem
                    },
                    '-',
                    {
                        'text': 'Mover',
                        'iconCls': 'icon-core icon-core-move-fold',
                        'scope': this,
                        'handler': this.moveItem
                    },
                    '-',
                    '->',
                    '-',
                    {
                        'text': 'Atualizar',
                        'iconCls': 'x-tbar-loading',
                        'scope': this,
                        'handler': function() {
                            var selected = core.nullValue(
                                this.getSelectionModel().getSelectedNode(),
                                this.getRootNode()
                            );

                            if(!selected.leaf) selected.reload();
                            else selected.parentNode.reload();
                        }
                    }
                ]
            });

        return this._toolbar;
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        if(cfg.restWindow)
            this.restWindow = cfg.restWindow;

        if(cfg.folderIndexField)
            this.folderIndexField = cfg.folderIndexField;

        Ext.applyIf(
            cfg,
            {
                'containerScroll': true,
                'rootVisible': false,
                'autoScroll': true,
                'disableNode': undefined,
                'root': {
                    'text': 'Root',
                    'leaf': false,
                    'id': '0'
                }
            }
        );

        Ext.apply(
            cfg,
            {
                'tbar': this.getToolbar(),
                'loader': this.getLoader()
            }
        );

        // this.callParent([cfg]);
        core.RestfulTree.superclass.constructor.call(this, cfg);

        if(this.disableNode) {
            var sm = this.getSelectionModel()
            sm.on({
                'scope': this,
                'beforeselect': function(tree, node) {
                    if(node.id == this.disableNode)
                        return false;
                    else
                        return true
                }
            });

            this.on({
                'scope': this,
                'load': function(node) {
                    Ext.each(
                        node.childNodes,
                        function(childNode) {
                            if(childNode.id == this.disableNode) {
                                childNode.isExpandable = function() {
                                    return false;
                                }
                                childNode.disable();
                            }
                        },
                        this
                    );
                }
            })
        }
    }
})
