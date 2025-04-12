var storeCache = {};
Ext._define('raf.activity.AllActivitieswindow', {
    extend: 'Ext.Window',

    factoryStore: function(cfg) {
        this._factoryStore = Ext._create('Ext.data.Store', {
            autoLoad: true,
            proxy: Ext._create('Ext.data.HttpProxy', {
                url: core.callAction('RAFActivity', 'all_activities')
            }),
            baseParams: {
                'activity': cfg.params.activity,
            },
            reader: Ext._create('Ext.data.JsonReader', {
                totalProperty: 'count',
                root: 'collection',
                fields: [
                    {name: 'activity', type: 'int'},
                    {name: 'month_year', type: 'string'},
                    {name: 'employee_matricula', type: 'int'},
                    {name: 'employee_unicode', type: 'string'},
                    {name: 'amount', type: 'int'},
                ]
            })
        });
        this._factoryStore.load({
            'scope': this,
            'callback': function() {
                this.getFormPanel().getForm().setValues({
                    total: storeCache.reader.jsonData.total,
                });
            }
        });
        return this._factoryStore;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = new Ext.grid.ColumnModel({
                columns: [
                    {header: 'RAF', width: 100, sortable: false, dataIndex: 'month_year', menuDisabled: true, resizable: false, align: 'center'},
                    {header: 'Matrícula', width: 85, sortable: false, dataIndex: 'employee_matricula', menuDisabled: true, resizable: false, align: 'center'},
                    {header: 'Membro', width: 550, sortable: false, dataIndex: 'employee_unicode', menuDisabled: true, resizable: false,},
                    {header: 'Qtd', width: 50, sortable: false, dataIndex: 'amount', menuDisabled: true, resizable: false},
                    {header: '', xtype: 'actioncolumn', align: 'center', width: 25, scope: this, menuDisabled: true,
                        items: [
                            {
                                tooltip: 'Ver documentos',
                                icon: '/'+ global.Context + '/static/images/icons/select.png',
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
                        ]
                    }
                ],
            });
        return this._columnModel;

    },

    getActivitiesGrid: function(cfg) {
        if(!this._activitiesGrid)
            this._activitiesGrid = Ext._create('Ext.grid.GridPanel', {
                store: this.factoryStore(cfg),
                colModel: this.getColumnModel(),
                height: 195,
                frame: true,
                iconCls: 'icon-grid',
            });
        return this._activitiesGrid;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'fieldset',
                        title: 'Atividade',
                        collapsible: false,
                        autoHeight:true,
                        items:[
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'column',
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 220,
                                        columnWidth: 0.8,
                                        items: [
                                            {
                                                xtype: 'displayfield',
                                                fieldLabel: 'Promotoria',
                                                name: 'workerlocation',
                                                hideLabel: true,
                                            },
                                            {
                                                xtype: 'displayfield',
                                                fieldLabel: 'Questionário',
                                                name: 'quiz',
                                                hideLabel: true,
                                            },
                                            {
                                                xtype: 'displayfield',
                                                fieldLabel: 'Assunto',
                                                name: 'item',
                                                hideLabel: true,
                                            },
                                            {
                                                xtype: 'displayfield',
                                                fieldLabel: 'Movimento',
                                                name: 'subitem',
                                                hideLabel: true,
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 220,
                                        columnWidth: 0.2,
                                        items: [
                                            {
                                                xtype:'fieldset',
                                                title: 'TOTAL',
                                                collapsible: false,
                                                autoHeight:true,
                                                items:[
                                                    {
                                                        xtype: 'displayfield',
                                                        name: 'total',
                                                        hideLabel: true,
                                                        width: '100%',
                                                        style: {textAlign: 'center', fontSize: '24px', fontWeight: 'bold'},
                                                    },
                                                ]
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                    this.getActivitiesGrid(cfg)
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {

        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Visualizar todos os lançamentos para promotoria',
            width: 910,
            height: 350,
            modal: true,
        });
        Ext.apply(cfg, {
            items: this.getFormPanel(cfg),
            buttons: [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });
        raf.activity.AllActivitieswindow.superclass.constructor.call(this, cfg);
        this.getFormPanel(cfg).getForm().setValues(
            {
                workerlocation: cfg.params.workerlocation,
                quiz: cfg.params.quiz,
                item: cfg.params.item,
                subitem: cfg.params.subitem,
                total: '000',
            }
        );
        storeCache = this.factoryStore(cfg);
    }
});
