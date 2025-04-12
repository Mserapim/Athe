Ext._define('judicial.ScopeTree', {
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
                                                'proc-devolvidos',
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

    _getNodeCollaboration: function(){
      if(!this._rootCollaboration)
          this._rootCollaboration = Ext._create('Ext.tree.TreeNode', {
              text: 'COLABORAÇÕES',
              iconCls:'icon-judicial icon-ejud-open-proccess',
              leaf: false
            }
          );
      return this._rootCollaboration;
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
        var node_collaboration = this._getNodeCollaboration()

        Ext.Ajax.request({
            url: core.callAction('EJudWorkplaceRestful', 'locations_of_work'),
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

                            if(record.is_collaboration)
                              node_collaboration.appendChild(node);
                            else
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
              root.appendChild(node_collaboration);
            }
        });
    },

    openTagManageWindow: function() {
        if(this.locationSelected())
            Ext._create('judicial.TagManageWindow', {
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

    openMovementReportWindow: function() {
        var wnd = Ext._create('judicial.reports.MovementReportWindow', {
            modal: true,
            title: 'Relatório de Movimentações'
        });

        wnd.getFormPanel().getForm().setValues({
            workplace: this.locationSelected()
        });

        wnd.show();
    },

    openMovementReportWindowWithoutMembers: function() {
        var wnd = Ext._create('judicial.reports.MovementReportWindowWithoutMembers', {
            modal: true,
            title: 'Relatório de Movimentações Por Servidor'
        });

        wnd.getFormPanel().getForm().setValues({
            workplace: this.locationSelected()
        });

        wnd.show();
    },

    openInstaurationRerportWidow: function() {
        var wnd = Ext._create('judicial.reports.InstaurationReportWindow', {
            modal: true,
            title: 'Relatório de Instaurações'
        });

        wnd.getFormPanel().getForm().setValues({
            workplace: this.locationSelected()
        });

        wnd.show();
    },

    openMovementCnmpRerportWidow: function() {
        var wnd = Ext._create('judicial.reports.CnmpReportWindow', {
            modal: true,
            title: 'Dados e Estatística da Movimentação Processual Por Unidade'
        });

        wnd.getFormPanel().getForm().setValues({
            workplace: this.locationSelected()
        });

        wnd.show();
    },

    openProgressReportWindow: function() {
        var wnd = Ext._create('judicial.reports.ProgressReportWindow', {
            modal: true,
            title: 'Relatório quantitativo dos procedimentos em trâmite'
        });

        wnd.getFormPanel().getForm().setValues({
            workplace: this.locationSelected()
        });

        wnd.show();
    },

    getTopBar: function(cfg){
      return [
          {
              toolTip: 'Localizador',
              iconCls: 'icon-judicial icon-ejud-open-bookmark',
              scope: this,
              handler: function() {this.openTagManageWindow();}
          },
          '-',
          {
              toolTip: 'Relatórios',
              iconCls: 'icon-core icon-core-reports',
              menu: [
                  {
                      text: 'Relatório de Instaurações',
                      scope: this,
                      handler: function() { this.openInstaurationRerportWidow(); }
                  },
                  {
                      text: 'Relatório de Movimentações',
                      scope: this,
                      handler: function() { this.openMovementReportWindow(); }
                  },
                  {
                      text: 'Relatório de Movimentações Por Servidor',
                      scope: this,
                      handler: function() { this.openMovementReportWindowWithoutMembers(); }
                  },
                  {
                      text: 'Quantitativo dos procedimentos em trâmite',
                      scope: this,
                      handler: function() { this.openProgressReportWindow(); }
                  },
                  {
                      text: 'Dados e Estatística da Movimentação Processual Por Unidade',
                      scope: this,
                      handler: function() { this.openMovementCnmpRerportWidow(); }
                  },
              ],
              hidden: (cfg.hiddenReportAction || false)
          },
          '-',
          '->',
          '-',
          {
              toolTip: 'Refresh',
              iconCls: 'icon-core icon-core-refresh',
              scope: this,
              handler: function(){
                  this.refresh()
              }
          },
          '-',
          {
              toolTip: 'Desmarcar Lotação',
              text: 'Desmarcar Lotação',
              iconCls: 'icon-core icon-core-delete',
              scope: this,
              handler: function(){
                  Ext._create("judicial.Manage")
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
