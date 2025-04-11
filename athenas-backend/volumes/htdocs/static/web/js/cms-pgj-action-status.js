if(!toolkit.web.cms.pgjActionsStatus)
{
    toolkit.web.cms.pgjActionsStatus = Ext.extend(Ext.Window, {
        constructor: function()
        {
            var options = {
                title: 'Fases de atuação',
                layout: 'fit',
                closable: true,
                defaults: {margins: '2 2 2 2'},
                width: 360,
                height: 270
            };

            toolkit.web.cms.pgjActionsStatus.superclass.constructor.call(this, options);

            this.store = new Ext.data.JsonStore({
                autoLoad: true,
                root: 'result',
                totalProperty: 'total',
                remoteSort: true,
                fields: ['id', 'name'],
                url: action('CMS/get_prosecutor_action_statuses/json'),
            });

            new Ext.LoadMask(Ext.getBody(), {msg: 'Por favor aguarde...', store: this.store});
            this.add(this.getPGJActionStatuses());
            this.doLayout();
        },

        getPGJActionStatuses: function()
        {
            if(!this.statuses)
            {
                this.statuses = new Ext.grid.GridPanel({
                    scope: this,
                    store: this.store,
                    tbar:
                    [
                        {
                            tooltip:'Nova fase',
                            icon: icons+'add.png',
                            text: 'Nova',
                            handler: function()
                            {
                                this.makeForm({
                                    vals: {}
                                }).show();
                            },
                            scope: this
                        }
                    ],
                    columns:
                    [
                        {dataIndex: 'name', header: 'Fase', width: 285},
                        {
                            xtype: 'actioncolumn',
                            width: 50,
                            scope:this,
                            items: [
                                {
                                    tooltip: 'Editar',
                                    icon: icons+'edit.png',
                                    handler: function(grid, row, col)
                                    {
                                        var record = grid.getStore().getAt(row);
                                        this.makeForm({
                                            title: 'Editar atuação',
                                            vals: {
                                                id: record.get('id'),
                                                name: record.get('name')
                                            }
                                        }).show();
                                    },
                                    scope:this
                                },
                                {
                                    tooltip: 'Excluir',
                                    icon: icons+'delete.png',
                                    handler: function(grid, row, col)
                                    {
                                        var record = grid.getStore().getAt(row);

                                        xConfirm({
                                            title: 'Confirmação',
                                            msg: 'Confirma a exclusão da atuação: '+ record.get('name') +' ?',
                                            fn: function(btn)
                                            {
                                                deleteItem({
                                                    signal: btn,
                                                    model: 'ProsecutorActionStatus',
                                                    pars: record.get('id'),
                                                    store: grid.getStore()
                                                });
                                            }
                                        });
                                    }
                                }
                            ]
                        }
                    ],
                    bbar: new Ext.PagingToolbar({
                        store: this.store,
                        displayInfo: true,
                        pageSize: 20,
                        prependButtons: true
                    })
                });
            }
            return this.statuses;
        },

        makeForm: function(opts)
        {
            opts = opts || {}
            opts = Ext.apply({
                store: this.store,
                success: null
            }, opts);

            return new ExtFormHelper({
                url: action('CMS/add_or_edit_prosecutor_action_status/json'),
                store: opts.store,
                success: opts.success,
                windowConfig: {
                    title: opts.title || 'Adicionar fase',
                },
                formConfig: {
                    autoWidth: true,
                    autoHeight: true,
                    items: [
                        {
                            name: 'id',
                            value: opts.vals.id || '',
                            xtype: 'hidden'
                        },
                        {
                            name: 'name',
                            fieldLabel :'Fase',
                            value: toolkit.util.replaceAll(opts.vals.name, '\\', '') || '',
                            xtype: 'textfield',
                            width: 250
                        }
                    ]
                }
            });
        }
    });
}
