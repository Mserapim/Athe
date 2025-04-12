Ext._define('raf.FillActivity.Grid', {
    extend: 'Ext.grid.GridPanel',

    factoryStore: function(cfg) {
        return Ext._create('Ext.data.GroupingStore', {
            autoLoad: true,
            proxy: Ext._create('Ext.data.HttpProxy', {
                url: core.callAction('RAFQuiz', 'all_items')
            }),
            baseParams: {
                quiz: cfg.params.quiz,
                workerlocation: cfg.params.workerlocation
            },
            groupField: 'item_unicode',
            remoteSort: true,

            reader: Ext._create('Ext.data.JsonReader', {
                totalProperty: 'count',
                root: 'collection',
                fields: [
                    {name: 'item', type: 'int'},
                    {name: 'item_unicode', type: 'string'},
                    {name: 'subitem', type: 'int'},
                    {name: 'subitem_unicode', type: 'string'},
                    {name: 'subitem_description', type: 'string'},
                    // {name: 'subitem_list_taxonomy', type: 'string'},
                    {name: 'subitem_tooltip', type: 'string'},
                    {name: 'subitem_typeicons'},
                    {name: 'activity', type: 'int'},
                    {name: 'activity_amount_submitted', type: 'int'},
                    {name: 'activity_amount', type: 'int'},
                    {name: 'workerlocation_monthyear', type: 'string'},
                    {name: 'icons'},
                    // {name: 'adjustment'},
                    {name: 'manual_amount', type: 'bool'},
                    {name: 'blocked', type: 'bool'},
                    {name: 'item_number_order', type: 'int'},
                    {name: 'conf_activities_maintenance', type: 'int'},
                ]
            })
        });
    },

    openTaxonomy: function(grid, row, col) {
        grid.getSelectionModel().selectRow(row);
        var record = grid.getStore().getAt(row);
        return Ext._create('raf.ViewTaxonomyWindow', {
            params: {
                activity: record.data.activity,
            }
        }).show();
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = new Ext.grid.ColumnModel({
                columns: [
                    {header: 'Contagem', dataIndex: 'subitem_typeicons', width: 10, renderer: core.rendererIconGrid, menuDisabled: true, align: 'center'},
                    {header: 'Itens/Sub-Itens', width: 75, sortable: false, dataIndex: 'subitem_unicode', hideable: false,
                         renderer: function(value, metaData, record) {
                           txt = '<div ext:qtip="' + record.get('subitem_tooltip') + '">' + value + '</div>';
                          return txt;
                         },
                     },
                    {dataIndex: 'item_unicode', menuDisabled: true},
                    {header: 'Qtd', width: 5, sortable: false, dataIndex: 'activity_amount', menuDisabled: true, align: 'center'},
                    {header: 'Status', dataIndex: 'icons', width: 5, renderer: core.rendererIconGrid, menuDisabled: true, align: 'center'},
                    {header: '', xtype: 'actioncolumn', align: 'center', width: 12, scope: this, menuDisabled: true,
                        items: [
                            {
                                tooltip: 'Ver documentos do membro',
                                icon: '/'+ global.Context + '/static/images/icons/reports.png',
                                scope:this,
                                handler: function(grid, row, col) {
                                    grid.getSelectionModel().selectRow(row);
                                    var record = grid.getStore().getAt(row);

                                    Ext._create('raf.autoreference.DetailWindow', {
                                        params: {
                                            activity: record.data.activity
                                        }
                                    }).show();
                                }
                            },
                            {
                                tooltip: 'Ver todos os registros da promotoria',
                                icon: '/'+ global.Context + '/static/images/icons/copy.png',
                                scope:this,
                                handler: function(grid, row, col) {
                                    grid.getSelectionModel().selectRow(row);
                                    var record = grid.getStore().getAt(row);

                                    Ext._create('raf.activity.AllActivitieswindow', {
                                        params: {
                                            workerlocation: this.params.workerlocation_unicode,
                                            quiz: this.params.quiz_unicode,
                                            item: record.data.item_unicode,
                                            subitem: record.data.subitem_unicode,
                                            activity: record.data.activity
                                        },
                                    }).show();
                                }
                            },
                            {
                                tooltip: 'Ver Classificação taxonômica',
                                icon: '/'+ global.Context + '/static/images/icons/info.png',
                                scope:this,
                                handler: function(grid, row, col) {
                                    grid.getSelectionModel().selectRow(row);
                                    var record = grid.getStore().getAt(row);

                                    Ext._create('raf.ViewTaxonomyWindow', {
                                        params: {
                                            quiz_id: this.params.quiz,
                                            item_id: record.data.item,
                                            subitem_id: record.data.subitem,
                                        }
                                    }).show();
                                }
                            },
                        ]
                    }
                ],
            });

        return this._columnModel;

    },

    factoryWindow: function(cfg) {
        return Ext._create('raf.FillAdjustmentManageWindow', cfg);
    },

    makeConfig: function(record) {
        var conf = {};

        Ext.apply(
            conf,
            {
                modal: true,
                values: {
                    adjustment: 0,
                    workerlocation: this.params.workerlocation,
                    workerlocation_unicode: this.params.workerlocation_unicode,
                    item: record.data.item,
                    item_unicode: record.data.item_unicode,
                    subitem: record.data.subitem,
                    subitem_unicode: record.data.subitem_unicode,
                    subitem_description: record.data.subitem_tooltip,
                    activity_amount_submitted: record.data.activity_amount_submitted,
                    activity_amount: record.data.activity_amount,
                    workerlocation_monthyear: record.data.workerlocation_monthyear,
                    activity: record.data.activity,
                    manual_amount: record.data.manual_amount,
                    blocked: record.data.blocked,
                    conf_activities_maintenance: record.data.conf_activities_maintenance,
                    quiz: this.params.quiz,
                    quiz_unicode: this.params.quiz_unicode,
                    // quiz_list_classes: this.params.quiz_list_classes,
                    gridMain: this,
                },
                callback: {
                    success: {
                        scope: this,
                        fn: function(instance) {
                            core.invokeCallback((this.callback || {}).success);
                            this.getStore().load({});
                        }
                    }
                }
            }
        );

        return conf;
    },

    openActivityWindow: function(cfg) {
        var values = {
            modal: true,
            params: {
                manual_amount: cfg.get('manual_amount'),
                blocked: cfg.get('blocked'),
            },
            callback: {
                success: {
                    scope: this,
                    fn: function(instance) {
                        core.invokeCallback((this.callback || {}).success);
                        this.getStore().load({});
                    }
                }
            }
        };
        if(cfg.get('activity'))
            Ext.applyIf(
                values,
                {
                    action: 'update',
                    values: 'remote',
                    oId: cfg.get('activity')
                }
            );
        else
            Ext.applyIf(
                values,
                {
                    action: 'create',
                    values: {
                        workerlocation: this.params.workerlocation,
                        workerlocation_unicode: this.params.workerlocation_unicode,
                        item: cfg.get('item'),
                        item_unicode: cfg.get('item_unicode'),
                        subitem: cfg.get('subitem'),
                        subitem_unicode: cfg.get('subitem_unicode'),
                        quiz: this.params.quiz,
                        quiz_unicode: this.params.quiz_unicode,
                    }

                }
            );


        Ext._create('raf.activity.Window', values).show();
    },

    doubleClickFunction: function(grid) {
        var selected = grid.getSelectionModel().getSelected();
        console.log(selected.data);
        if (selected.data.conf_activities_maintenance == 1) {
            if(selected)
                this.openWindow(selected);
        } else {
            Ext.Msg.show({
                title: 'Lançar Atividades',
                msg: 'Alteração nas atividades não permitida.<br />Para esclarecimentos entrar em contato com a Corregedoria-geral.',
                icon: Ext.Msg.INFO,
                buttons: Ext.Msg.OK
            });
        }
    },

    openWindow: function(record) {
        // if (record.data.subitem_unicode=='SALDO ANTERIOR' && record.data.workerlocation_monthyear=='012018') {
        //     this.factoryWindow(this.makeConfig(record)).show();
        // } else {
            if (record.data.blocked) {
                Ext.Msg.show({
                    title: 'Lançar Atividades',
                    msg: 'Movimento bloqueado para edição.<br />Movimento calculado automaticamente.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            } else {
                if(record.data.manual_amount)
                    this.openActivityWindow(record);
                else
                    this.factoryWindow(this.makeConfig(record)).show();
            }
        // }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                frame: false
            }
        );

        Ext.apply(
            cfg,
            {
                loadMask: true,
                ds: this.factoryStore(cfg),
                colModel: this.getColumnModel(),
                view: new Ext.grid.GroupingView({
                    startCollapsed: true,
                    forceFit: true,
                    showGroupName: false,
                    enableNoGroups: false,
                    enableGroupingMenu: false,
                    hideGroupedColumn: true
                }),
                listeners: {
                    scope: this,
                    dblclick: function(evt) {
                        this.doubleClickFunction(this);
                    }
                }
            }
        );
        raf.FillActivity.Grid.superclass.constructor.call(this, cfg);

    }
});
