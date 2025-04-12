var storeCache = {};

Ext._define('raf.adjustment.AdjustmentAnalysisInternalControlWindow', {
    extend: 'core.RestfulWindow',
    // extend: 'Ext.Window',

    rest: 'raf.adjustment.BaseRestful',

    factoryStore: function(cfg) {
        if(!this._factoryStore) {
            this._factoryStore = Ext._create('Ext.data.Store', {
                  autoLoad: true,
                  proxy: Ext._create('Ext.data.HttpProxy', {
                      url: core.callAction('RAFActivityAdjustmentInternalControl', 'get_adjustment')
                  }),
                  baseParams: {
                      adjustment: cfg.params.adjustment,
                  },
                  reader: Ext._create('Ext.data.JsonReader', {
                      totalProperty: 'count',
                      root: 'collection',
                      fields: [
                          {name: 'adjustment_pk', type: 'auto'},
                          {name: 'adjustment_situation', type: 'auto'},
                          {name: 'raf_monthyear', type: 'auto'},
                          {name: 'employee_unicode', type: 'auto'},
                          {name: 'workerlocation_unicode', type: 'auto'},
                          {name: 'quiz_unicode', type: 'auto'},
                          {name: 'item_unicode', type: 'auto'},
                          {name: 'subitem_unicode', type: 'auto'},
                          {name: 'activity_amount_submitted', type: 'auto'},
                      ]
                  })
              });
              storeCache = this._factoryStore;
              this._factoryStore.load({
                    'scope': this,
                    'callback': function() {
                        this.getFormPanel().getForm().setValues(storeCache.data.items["0"].data);
                        this.adjustment = storeCache.data.items["0"].data.adjustment_pk;
                        this.getDataAdjustmentGrid().setParam('activityadjustment', this.adjustment);
                        this.getDataAdjustmentGrid().setFilterProperty('activityadjustment', this.adjustment, 101, true);
                        this.getDataAdjustmentGrid().getStore().reload();
                    },
              });
          }
          return this._factoryStore;
    },

    getNewAmount: function(cfg) {
        var rest = this.factoryRestful();
        if (this.adjustment) {
            rest.newAmount(
                {
                    adjustment: this.adjustment,
                },
                {
                    scope: this,
                    fn: function(rst) {
                        if(rst.success) {
                            this.getFormPanel(cfg).getForm().setValues(
                                {activity_amount: rst.newAmount, }
                            );
                        }
                        else
                        Ext.Msg.show({
                            title: 'Recálculo da nova quantidade',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {
                    scope: this,
                    fn: function(message) {
                        Ext.Msg.show({
                            title: 'Recálculo da nova quantidade',
                            msg: message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {
                    scope: this,
                    fn: function() {
                    }
                }
            );
        }
    },

    getDataAdjustmentGrid: function(cfg) {
        if(!this._dataAdjustmentGrid) {
            this._dataAdjustmentGrid = Ext._create('raf.adjustment.dataadjustment.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 445,
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['add', 'edit', 'remove', 'download', 'search', 'response'],
                 configOrderToolBar: ['searchProcessNumber', '->', 'accept', 'requestInformation', 'reject'],
                 doubleClickHandler: function() { },
            });
            this.getDataAdjustmentGrid().setFilterProperty('activityadjustment', 0, 101, true);
            this.getDataAdjustmentGrid().getStore().on({
                'load': {
                    scope: this,
                    fn: function(store, records) {
                        this.getNewAmount(cfg);
                        this.params.gridMain.getStore().reload();
                    }
                }
            });
        }
        return this._dataAdjustmentGrid;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        layout: 'form',
                        autoScroll: true,
                        overflow: 'auto',
                        items: [
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
                                        columnWidth: 0.70,
                                        items: [
                                            {
                                                xtype:'fieldset',
                                                title: 'RAF / Membro / Órgão de Execução / Atividade',
                                                collapsible: false,
                                                autoHeight: true,
                                                width: 673,
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
                                                                columnWidth: 0.08,
                                                                items: [
                                                                    {
                                                                        xtype: 'displayfield',
                                                                        fieldLabel: 'RAF:',
                                                                        name: 'raf_monthyear',
                                                                        hideLabel: true,
                                                                        style: {fontWeight: 'bold', },
                                                                    },
                                                                ]
                                                            },
                                                            {
                                                                xtype:'panel',
                                                                autoHeight:true,
                                                                layout: 'form',
                                                                labelWidth: 220,
                                                                columnWidth: 0.90,
                                                                items: [
                                                                    {
                                                                        xtype: 'displayfield',
                                                                        fieldLabel: 'Membro:',
                                                                        name: 'employee_unicode',
                                                                        hideLabel: true,
                                                                        style: {fontWeight: 'bold', },
                                                                    },
                                                                ]
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype: 'displayfield',
                                                        fieldLabel: 'Promotoria',
                                                        name: 'workerlocation_unicode',
                                                        hideLabel: true,
                                                        style: {fontWeight: 'bold', },
                                                    },
                                                    {
                                                        xtype: 'displayfield',
                                                        fieldLabel: 'Promotoria',
                                                        name: 'workerlocation_unicode',
                                                        hideLabel: true,
                                                        style: {fontWeight: 'bold', },
                                                    },
                                                    {
                                                        xtype: 'displayfield',
                                                        fieldLabel: 'Questionário',
                                                        name: 'quiz_unicode',
                                                        hideLabel: true,
                                                        style: {fontWeight: 'bold', },
                                                    },
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
                                                                columnWidth: 0.5,
                                                                items: [
                                                                    {
                                                                        xtype: 'displayfield',
                                                                        fieldLabel: 'Item',
                                                                        name: 'item_unicode',
                                                                        hideLabel: true,
                                                                        style: {fontWeight: 'bold', },
                                                                    },
                                                                ]
                                                            },
                                                            {
                                                                xtype:'panel',
                                                                autoHeight:true,
                                                                layout: 'form',
                                                                labelWidth: 220,
                                                                columnWidth: 0.5,
                                                                items: [
                                                                    {
                                                                        xtype: 'displayfield',
                                                                        fieldLabel: 'SubItem',
                                                                        name: 'subitem_unicode',
                                                                        hideLabel: true,
                                                                        style: {fontWeight: 'bold', },
                                                                    },
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        xtype: 'hidden',
                                                        name: 'activity',
                                                    },
                                                ]
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 220,
                                        columnWidth: 0.15,
                                        items: [
                                            {
                                                xtype:'fieldset',
                                                title: 'QUANTIDADE ATUAL',
                                                collapsible: false,
                                                height: 119,
                                                width: 140,
                                                items:[
                                                    {
                                                        xtype: "displayfield",
                                                        name: "activity_amount_submitted",
                                                        hideLabel: true,
                                                        width: '100%',
                                                        style: {textAlign: 'center', fontSize: '72px', fontWeight: 'bolder', color: 'blue'},
                                                    },
                                                ]
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 220,
                                        columnWidth: 0.15,
                                        items: [
                                            {
                                                xtype:'fieldset',
                                                title: 'NOVA QUANTIDADE',
                                                collapsible: false,
                                                height: 119,
                                                width: 140,
                                                items:[
                                                    {
                                                        xtype: "displayfield",
                                                        id: "new-amount-displayfield",
                                                        name: "activity_amount",
                                                        hideLabel: true,
                                                        width: '100%',
                                                        style: {textAlign: 'center', fontSize: '72px', fontWeight: 'bolder', color: 'red'},
                                                    },
                                                ]
                                            },
                                        ]
                                    }
                                ]
                            },
                            {
                                xtype:'fieldset',
                                title: 'Alterações solicitadas',
                                collapsible: false,
                                collapsed: false,
                                autoHeight:true,
                                width: 965,
                                items:[
                                    this.getDataAdjustmentGrid(cfg),
                                ]
                            },
                        ]
                    },
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
        this.adjustment = 0;
        Ext.applyIf(cfg, {
            title: 'Análise de Solicitação de Ajuste',
            width: 1000,
            height: 685,
        });
        Ext.apply(cfg, {
            ds: this.factoryStore(cfg),
            items: this.getFormPanel(),
        });
        raf.adjustment.AdjustmentAnalysisInternalControlWindow.superclass.constructor.call(this, cfg);
        storeCache = this.factoryStore(cfg);
    }
});
