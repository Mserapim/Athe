toolkit.web.cms.Polls = Ext.extend(Ext.Window, {
    constructor: function(site, permissions, title, show)
    {
        this.site = site;
        toolkit.web.cms.Polls.superclass.constructor.call(this, {
            title: 'Enquetes em '+title,
            layout: 'fit',
            height: 350,
            width: 500,
            items: [this._getPollsGrid()],
            tbar: [
                {
                    tooltip: 'Criar nova enquete.',
                    icon: icons+'add.png',
                    text: 'Nova',
                    handler: function()
                    { this._makeForm({title: 'Criar Enquete', vals: {area: this.site}}).show(); },
                    scope:this
                },
                '-',
                {
                    tooltip: 'Sites',
                    icon: icons+'applications-internet.png',
                    text: 'Sites',
                    handler: function()
                    {
                        getSiteManager(true, permissions);
                        toolkit.web.cms.pollManager.hide();
                    },
                    scope: this
                }
            ],
            bbar: [this._getPollsPagination()],
            listeners: {
                show:function()
                { new Ext.LoadMask(this.getEl(), {msg: 'Por favor aguarde...', store: this._getPollsStore()}); }
            }
        });
    },

    _getPollsStore: function()
    {
        if(!this._pollsStore)
        {
            this._pollsStore = new Ext.data.JsonStore({
                autoLoad: true,
                root: 'result',
                totalProperty: 'total',
                fields: ['id', 'content', 'title', 'slug', 'show_partial', 'create_date', 'position',
                'published', 'published_date', 'publication_start', 'publication_end', 'can_edit'],
                proxy: new Ext.data.HttpProxy({
                    method: 'GET',
                    url: action('Polls/list/json')
                }),
                baseParams: {start: 0, limit: 50, area: this.site},
                scope: this,
                listeners: {
                    load: function()
                    {
                        Ext.select('.athenas-published').set({src: icons+'published.png'});
                        Ext.select('.athenas-non-published').set({src: icons+'no-published.png'});
                        Ext.select('.athenas-edit').set({src: icons+'edit.png'});
                        Ext.select('.athenas-delete').set({src: icons+'delete.png'});
                    }
                }
            });
        }
        return this._pollsStore;
    },

    _getPollsPagination: function()
    {
        if(!this._pollsPagination)
        {
            this._pollsPagination = new Ext.PagingToolbar({
                store: this._getPollsStore(),
                displayInfo: true,
                pageSize: 15,
                prependButtons: true
            });

        }
        return this._pollsPagination;
    },

    _getPollsGrid: function()
    {
        if(!this._pollsGrid)
        {
            this._pollsGrid = new Ext.grid.GridPanel({
                scope: this,
                region: 'center',
                border: true,
                store: this._getPollsStore(),
                columns:
                [
                    {dataIndex: 'title', header: 'Enquete', width: 368},
                    {
                        xtype: 'actioncolumn',
                        header:'Controles',
                        width: 100,
                        scope: this,
                        items:
                        [
                            {
                                tooltip: 'Publicação de enquete',
                                getClass: function(v, meta, rec, a, b)
                                { return rec.get('published') ? 'athenas-published' : 'athenas-non-published'; },
                                handler: function(grid, row, col)
                                {
                                    var pubForm = makePublicationForm({
                                        title: 'Publicação de Enquete',
                                        store: grid.getStore(),
                                        record: grid.getStore().getAt(row)
                                    });
                                },
                                scope: this
                            },
                            {
                                tooltip: 'Alternativas da enquete',
                                icon: icons+'choice.png',
                                handler: function(grid, row, col)
                                {
                                    var r = grid.getStore().getAt(row)
                                    new toolkit.web.cms.Choices(r.get('id'), r.get('title')).show()
                                },
                                scope: this
                            },
                            // {
                            //     tooltip: 'Resultado',
                            //     icon: icons + 'report.png',
                            //     handler: function(grid, row, col)
                            //     {
                            //         var r = grid.getStore().getAt(row);
                            //         new toolkit.widget.ExtReportBuild('PollReport', '/to/mpe/web/enquete/resultado_enquete').runReport(
                            //             '', { enquete: r.get('content') }
                            //         );
                            //     }
                            // },
                            {
                                tooltip: 'Editar ou visualizar enquete',
                                iconCls: 'athenas-edit',
                                // getClass: function(v, meta, rec, a, b)
                                // { return rec.get('can_edit') ? 'athenas-edit' : ''; },
                                handler: function(grid, row, col)
                                {
                                    var r = grid.getStore().getAt(row)
                                    this._makeForm({
                                        title: 'Editar enquete',
                                        vals: {
                                            id: r.get('id'),
                                            area: this.site,
                                            title: r.get('title'),
                                            show_partial: r.get('show_partial'),
                                            // target: (r.get('target').length > 0) ? r.get('target')[0] : {id:0, description:'Todos'}
                                        }
                                    }).show();
                                },
                                scope: this
                            },
                            {
                                tooltip: 'Excluir enquete',
                                iconCls: 'athenas-delete',
                                // getClass: function(v, meta, rec, a, b)
                                // { return rec.get('can_edit') ? 'athenas-delete' : ''; },
                                handler: function(grid, row, col)
                                {

                                    var rec = grid.getStore().getAt(row);
                                    xConfirm({
                                        title: 'Confirmação',
                                        msg: 'Confirma a exclusão da enquete: '+ rec.get('title') +' ?',
                                        fn: function(btn)
                                        {
                                            deleteItem({
                                                signal: btn,
                                                model: 'Poll',
                                                pars: rec.get('id'),
                                                store: grid.getStore()
                                            });
                                        }
                                    });

                                },
                                scope: this
                            }
                        ]
                    }
                ]
            });
        }
        return this._pollsGrid;
    },

    _makeForm: function(opts)
    {
        return ExtFormHelper({
            url: action('Polls/add_or_edit/json'),
            store: this._getPollsStore(),
            windowConfig: {
                title: opts.title
            },
            formConfig: {
                autoWidth: true,
                autoHeight: true,
                items: [
                    {
                        id: 'area',
                        name: 'area',
                        value: opts.vals.area || '',
                        xtype: 'hidden'
                    },
                    {
                        id: 'id',
                        name: 'id',
                        value: opts.vals.id || '',
                        xtype: 'hidden'
                    },
                    {
                        id: 'title',
                        fieldLabel: 'Enquete',
                        name: 'title',
                        value: opts.vals.title || '',
                        width: 350,
                        xtype: 'textfield'
                    },
                    {
                        id: 'show_partial',
                        fieldLabel: 'Mostrar resultado parcial?',
                        name: 'show_partial',
                        checked: opts.vals.show_partial,
                        value: opts.vals.show_partial || '',
                        width: 350,
                        xtype: 'checkbox'
                    }
                ]
            }
        });
    }
});

toolkit.web.cms.Choices = Ext.extend(Ext.Window, {
    constructor: function(poll, title)
    {
        this.poll = poll;
        toolkit.web.cms.Choices.superclass.constructor.call(this, {
            title: 'Alternativas da enquete ' + title,
            layout: 'fit',
            modal: true,
            height: 350,
            width: 500,
            items: [this._getChoicesGrid()],
            tbar: [
                {
                    tooltip: 'Criar alternativa.',
                    icon: icons + 'add.png',
                    text: 'Nova',
                    handler: function()
                    { this._makeForm({title: 'Criar Alternativa', vals: {poll: this.poll}}).show(); },
                    scope: this
                }
            ],
            bbar: [this._getChoicesPagination()],
        });

    },

    _getChoicesStore: function()
    {
        if(!this._choicesStore)
        {
            this._choicesStore = new Ext.data.JsonStore({
                autoLoad: true,
                root: 'result',
                totalProperty: 'total',
                fields: ['id', 'choice', 'votes', 'percent', 'can_edit'],
                proxy: new Ext.data.HttpProxy({
                    method: 'GET',
                    url: action('Polls/choices/json')
                }),
                baseParams: {start: 0, limit: 50, poll: this.poll },
                listeners: {
                    load: function()
                    {
                        Ext.select('.athenas-edit').set({src: icons + 'edit.png'});
                        Ext.select('.athenas-delete').set({src: icons + 'delete.png'});
                    }
                }
            });
        }
        return this._choicesStore;
    },

    _getChoicesPagination: function()
    {
        if(!this._choicesPagination)
        {
            this._choicesPagination = new Ext.PagingToolbar({
                store: this._getChoicesStore(),
                displayInfo: true,
                pageSize: 15,
                prependButtons: true
            });

        }
        return this._choicesPagination;
    },

    _getChoicesGrid: function()
    {
        if(!this._choicesGrid)
        {
            this._choicesGrid = new Ext.grid.GridPanel({
                scope: this,
                region: 'center',
                border: true,
                store: this._getChoicesStore(),
                columns:
                [
                    {dataIndex: 'choice', header: 'Alternativa', width: 300},
                    {dataIndex: 'votes', header: 'Votos', width: 50},
                    {dataIndex: 'percent', header: 'Percentual', width: 70},
                    {
                        xtype: 'actioncolumn',
                        header: 'Controles',
                        width: 60,
                        scope: this,
                        items:
                        [
                            {
                                tooltip: 'Editar ou visualizar alternativa',
                                iconCls: 'athenas-edit',
                                // getClass: function(v, meta, rec, a, b)
                                // { return rec.get('can_edit') ? 'athenas-edit' : ''; },
                                handler: function(grid, row, col)
                                {
                                    var r = grid.getStore().getAt(row)
                                    this._makeForm({
                                        title: 'Editar alternativa',
                                        vals: {
                                            id: r.get('id'),
                                            poll: this.poll,
                                            choice: r.get('choice')
                                        }
                                    }).show();
                                },
                                scope: this
                            },
                            {
                                tooltip: 'Excluir alternativa',
                                iconCls: 'athenas-delete',
                                // getClass: function(v, meta, rec, a, b)
                                // { return rec.get('can_edit') ? 'athenas-delete' : ''; },
                                handler: function(grid, row, col)
                                {
                                    var rec = grid.getStore().getAt(row);
                                    xConfirm({
                                        title: 'Confirmação',
                                        msg: 'Confirma a exclusão da alternativa: '+ rec.get('choice') +' ?',
                                        fn: function(btn)
                                        {
                                            deleteItem({
                                                signal: btn,
                                                model: 'Choice',
                                                pars: rec.get('id'),
                                                store: grid.getStore()
                                            });
                                        }
                                    });

                                },
                                scope: this
                            }
                        ]
                    }
                ]
            });
        }
        return this._choicesGrid;
    },

    _makeForm: function(opts)
    {
        return ExtFormHelper({
            url: action('Polls/add_or_edit_choice/json'),
            store: this._getChoicesStore(),
            windowConfig: {
                title: opts.title,
                frame: true,
            },
            formConfig: {
                autoWidth: true,
                autoHeight: true,
                items: [
                    {
                        id: 'poll',
                        name: 'poll',
                        value: opts.vals.poll || '',
                        xtype: 'hidden'
                    },
                    {
                        id: 'id',
                        name: 'id',
                        value: opts.vals.id || '',
                        xtype: 'hidden'
                    },
                    {
                        id: 'choice',
                        fieldLabel: 'Alternativa',
                        name: 'choice',
                        value: opts.vals.choice || '',
                        width: 350,
                        xtype: 'textfield'
                    }
                ]
            }
        });
    }
});

toolkit.web.cms.showActivePolls = function(site)
{
    var store = new Ext.data.JsonStore({
        autoLoad: true,
        root: 'result',
        totalProperty: 'total',
        fields: ['id', 'title', 'voted', 'show_partial', 'choices', 'finished'],
        proxy: new Ext.data.HttpProxy({
            method: 'GET',
            url: action('Polls/list_active/json')
        }),
        baseParams: {start: 0, end: 15, area: site},
        listeners: {
            load: function(store)
            {
                var r = store.getAt(0);
                if( store.getCount() == 1 && !r.get('voted') && !r.get('finished'))
                {
                    toolkit.web.cms.activePoll({
                        title: 'Enquete',
                        store: store,
                        vals: {
                            poll: r.get('id'),
                            title: r.get('title'),
                            choices: r.get('choices'),
                            show_partial: r.get('show_partial')
                        }
                    }).show()
                }
                else if( store.getCount() > 1 )
                    new toolkit.web.cms.activePolls(site).show();
            }
        }
    });
}


toolkit.web.cms.PollResult = Ext.extend(Ext.Window, {
    constructor: function(poll, title)
    {
        this.poll = poll;
        toolkit.web.cms.Choices.superclass.constructor.call(this, {
            title: 'Resultado parcial da enquete '+title,
            layout: 'fit',
            modal: true,
            height: 150,
            width: 460,
            items: [this._getChoicesGrid()]
        });
    },

    _getChoicesStore: function()
    {
        if(!this._choicesStore)
        {
            this._choicesStore = new Ext.data.JsonStore({
                autoLoad: true,
                root: 'result',
                totalProperty: 'total',
                fields: ['id', 'choice', 'votes', 'percentage'],
                proxy: new Ext.data.HttpProxy({
                    method: 'GET',
                    url: action('Polls/choices/json')
                }),
                baseParams: {start: 0, end: 50, poll: this.poll}
            });
        }
        return this._choicesStore;
    },

    _getChoicesGrid: function()
    {
        if(!this._choicesGrid)
        {
            this._choicesGrid = new Ext.grid.GridPanel({
                scope: this,
                region: 'center',
                border: true,
                store: this._getChoicesStore(),
                columns:
                [
                    {dataIndex: 'choice', header: 'Alternativa', width: 320},
                    {dataIndex: 'votes', header: 'Votos', width: 50},
                    {dataIndex: 'percentage', header: 'Percentual', width: 70}
                ]
            });
        }
        return this._choicesGrid;
    }
});
