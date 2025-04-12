Ext._define('judicial.secretary.workspace.ScopeTree', {
    extend: 'Ext.tree.TreePanel',

    loadTypeLawSuit: function(root, workplace) {
        var rest = Ext._create('judicial.TagRestful');

        rest.doRequest(
            rest.getRoute(
                'read',
                null,
                'GET',
                {
                    params: {
                        filter: Ext.encode(this._getFiltersTypeLawsuit(root.attributes.is_collaboration))
                    },
                    scope: this,
                    success: function(xhr) {               
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success) {
                            rst.collection.forEach(
                                function(row) {
                                    root.appendChild(
                                        new Ext._create('Ext.tree.TreeNode', {
                                            value: row.pk,
                                            node: row.slug,
                                            text: row.title,
                                            type: [
                                                'nao-recebido', 
                                                'urgente', 
                                                'caixa-da-secretaria',
                                                'proc-devolvidos'
                                            ].indexOf(row.slug) >= 0  ? 'bookmark_item' : 'type_lawsuit',
                                            leaf: true,
                                            iconCls: row.icon_cls,
                                            expandable: false
                                        })
                                    );
                                }
                            );
                        }

                        if(!root.attributes.is_collaboration)
                          this._addLocators(root, workplace);
                    }
                }
            )
        );
    },

    _getFiltersTypeLawsuit: function(is_collaboration){
      if(is_collaboration)
        return [
            {property: 'tag_type', value: 1, stage: 1},
            {property: 'classification__isnull', value: false, stage: 2},
        ]
      else
        return [
            {property: 'tag_type', value: 1, stage: 1}
        ]
    },

    _addLocators: function(node, workplace){
        node.appendChild(
            Ext._create('Ext.tree.AsyncTreeNode', {
                value: null,
                node: 'bookmark',
                text: 'Localizadores',
                type: 'bookmark_root',
                leaf: false,
                expandable: true,
                loader: new Ext.tree.TreeLoader({
                    url: core.callAction('EJudTag', 'root', [workplace])
                }),
                iconCls: 'icon-judicial icon-ejud-bookmark',
                listeners: {
                    scope: this,
                    contextmenu: function(me, event) {
                        var menu = new Ext.menu.Menu({
                            items: [
                                this.getActions().manage,
                                '-',
                                {
                                    text: 'Recarregar',
                                    iconCls: 'icon-core icon-core-refresh',
                                    scope: this,
                                    handler: function() {
                                        me.reload();
                                    }
                                }
                            ]
                        });

                        menu.showAt([event.browserEvent.clientX, event.browserEvent.clientY]);

                        event.stopEvent();
                    },
                }
            })
        );
    },

    getActions: function(){
        if(!this.actions){
            this.actions = {};
            this.actions.manage = new Ext.Action({
                text: 'Gerenciar',
                iconCls: 'icon-core icon-core-run',
                tooltip: 'Gerenciar Marcadores',
                scope: this,
                handler: function(){this.openTagManageWindow();}
            });
        }

        return this.actions;
    },

    _addNodeSecretary: function (node) {
        node.appendChild(
            Ext._create('Ext.tree.TreeNode', {
                text: 'CAIXA DA SECRETARIA',
                type: 'type_lawsuit',
                iconCls: 'icon-judicial icon-ejud-procedimento-administrativo-in-grid',
                leaf: false
            })
        );
    },

    loadWorkLocations: function() {
        var root = this.getRootNode();

        Ext.Ajax.request({
            url: core.callAction('EJudWorkplaceRestful', 'secretaries_of_work'),
            scope: this,
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success) {
                    Ext.each(
                        rst.collection,
                        function(record) {
                            var node = Ext._create('Ext.tree.TreeNode', {
                                id: record.pk,
                                node: record.node,
                                text: record.description,
                                type: 'location',
                                is_collaboration: record.is_collaboration,
                                iconCls: record.icon
                            });
                            this.loadTypeLawSuit(node, record.pk);

                            root.appendChild(node);
                        },
                        this
                    );
                }
                else
                    Ext.Msg.show({
                        'title': 'Locais de Atuação',
                        'icon': Ext.Msg.ERROR,
                        'buttons': Ext.Msg.OK,
                        'msg': rst.message
                    });
            },
            failure: function(xhr) {
                Ext.Msg.show({
                    'title': 'Locais de Atuação',
                    'icon': Ext.Msg.ERROR,
                    'buttons': Ext.Msg.OK,
                    'msg': 'Ocorreu um erro tentando recuperar os locais de Trabalho.'
                });
            },
            callback: function(xhr) {
              
            }
        });
    },

    openTagManageWindow: function() {
        if(this.locationSelected())
            Ext._create('judicial.secretary.workspace.TagManageWindow', {
                action: 'create',
                modal: true,
                params: {
                    tag_type: 2,
                    work_place: this.locationSelected(),
                },
                callback: {
                    success: {
                        scope: this,
                        fn: function(instance) {
                            this.refresh();
                        }
                    }
                }
            }).show();
        else
            Ext.Msg.show({
                'title': 'Localizador',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Selecione um local de trabalho para criar o Localizador.'
            });
    },

    locationSelected: function(value) {
        if(value !== undefined)
            this._location = value;

        return this._location;
    },

    _refresh: function(value, search) {
        var search = core.nullValue(search, true);

        Ext.each(
            value,
            function(node) {
                if(search)
                    if(node.attributes.type=='location')
                        this._refresh(node.childNodes, false);
                    else
                        this._refresh(node.parentNode);
                else
                    if((node instanceof Ext.tree.AsyncTreeNode) && node.loaded)
                        node.reload();
            },
            this
        );

    },

    refresh: function() {
        var selection = this.getSelectionModel().getSelectedNode();
        this._refresh(selection);
    },

    getTopBar: function(cfg){
      return [
          '->',
          '-',
          {
              toolTip: 'Refresh',
              iconCls: 'icon-core icon-core-refresh',
              scope: this,
              handler: function(){
                  this.refresh()
              }
          }
      ]
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                tbar: this.getTopBar(cfg),
                rootVisible: false,
                root: Ext._create('Ext.tree.TreeNode', {
                    text: 'Atuação',
                    leaf: false
                }),
                listeners: {
                    scope: this,
                    render: this.loadWorkLocations
                }
            }
        );

        judicial.ScopeTree.superclass.constructor.call(this, cfg);
    }
});
