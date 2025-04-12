var storeCache = {};

Ext._define('raf.functionalactivityreport.HistoricRAFWindow', {
    extend: 'Ext.Window',

    factoryStore: function(cfg) {
        if(!this._factoryStore) {
            this._factoryStore = Ext._create('Ext.data.Store', {
                  autoLoad: true,
                  proxy: Ext._create('Ext.data.HttpProxy', {
                      url: core.callAction('RAFFunctionalActivityReport', 'get_historicRAF')
                  }),
                  baseParams: {
                      raf: cfg.params.raf,
                  },
                  reader: Ext._create('Ext.data.JsonReader', {
                      totalProperty: 'count',
                      root: 'collection',
                      fields: [
                          {name: 'action', type: 'auto'},
                          {name: "dt_action", dateFormat: "d/m/Y H:i", type: 'auto'},
                          {name: 'employee_unicode', type: 'auto'},
                      ]
                  })
              });

          }
          return this._factoryStore;

    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = new Ext.grid.ColumnModel({
                columns: [
                    {header: 'Data', width: 125, sortable: false, dataIndex: 'dt_action', menuDisabled: true, resizable: false, align: 'center'},
                    {header: 'Ação', width: 400, sortable: false, dataIndex: 'action', menuDisabled: true, resizable: false},
                    {header: 'Servidor', width: 400, sortable: false, dataIndex: 'employee_unicode', menuDisabled: true, resizable: false,},
                ],
            });
        return this._columnModel;

    },

    getHistoricRAFGrid: function(cfg) {
        if(!this._activitiesGrid)
            this._activitiesGrid = Ext._create('Ext.grid.GridPanel', {
                store: this.factoryStore(cfg),
                colModel: this.getColumnModel(),
                height: 330,
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
                        title: 'RAF',
                        collapsible: false,
                        autoHeight:true,
                        labelWidth: 50,
                        items:[
                            {
                                xtype: 'displayfield',
                                fieldLabel: 'Membro',
                                name: 'employee',
                                hideLabel: true,
                            },
                            {
                                xtype: 'displayfield',
                                fieldLabel: 'Mês/Ano',
                                name: 'month_reference',
                                hideLabel: false,
                            },
                        ]
                    },
                    this.getHistoricRAFGrid(cfg)
                ]
            });

        return this._formPanel;
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [

                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        this.close();
                    }
                }
            ];

        return this._buttons;
    },

    constructor: function(cfg) {

        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Histórico do RAF',
            width: 1000,
            height: 500,
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
        raf.functionalactivityreport.HistoricRAFWindow.superclass.constructor.call(this, cfg);
        this.getFormPanel(cfg).getForm().setValues(
            {
                employee: '<b>'+cfg.params.employee+'</b>',
                month_reference: '<b>'+cfg.params.month + '/' + cfg.params.year+'</b>',
            }
        );
    }
});
