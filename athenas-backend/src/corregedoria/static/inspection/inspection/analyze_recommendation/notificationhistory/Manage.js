Ext._define('corregedoria.inspection.inspection.follow_recommendation.notificationhistory.Manage', {
    extend: 'Ext.Window',

    getNotifyGrid: function() {
        if(!this._notifyGrid) {
            this._notifyGrid = Ext._create('corregedoria.inspection.inspection.follow_recommendation.notificationhistory.Grid', {
                region: 'north',
                title: 'Histórico de Noticações',
                height: 500,
                columnAction: false,
                configOrderToolBar: ['search'],
                hiddenFilter: true,
                doubleClickHandler: function() {},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true})
            });
        }
        return this._notifyGrid;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            {
                                xtype:'fieldset',
                                title: 'Inspeção/Correição',
                                collapsible: false,
                                collapsed: false,
                                autoHeight:true,
                                items:[
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 110,
                                        items: [
                                            {
                                                xtype: 'displayfield',
                                                name: 'execution_organ',
                                                fieldLabel: 'Órgão de Execução',
                                                style: {fontWeight: 'bold'},
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 155,
                                        items: [
                                            {
                                                xtype: 'displayfield',
                                                name: 'inspection_date',
                                                fieldLabel: 'Data da Inspeção/Correição',
                                                style: {fontWeight: 'bold'},
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype: 'tabpanel',
                        region: 'north',
                        activeTab: 0,
                        items: [
                            this.getNotifyGrid(),
                        ]
                    },
                ]
            });
        }
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
                },
            ];
        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            title: 'Histórico de Notificações de Atraso (via e-Doc)',
            width: 900,
            height: 700,
            modal: true,
        });
        Ext.apply(cfg, {
            items: [
                this.getFormPanel(cfg),
            ],
            buttons: this.getButtons(cfg),
        });
        corregedoria.inspection.inspection.follow_recommendation.notificationhistory.Manage.superclass.constructor.call(this, cfg);
        this.getFormPanel().getForm().setValues(
            {
                execution_organ: cfg.values.execution_organ,
                inspection_date: cfg.values.inspection_date_initial + ' à ' + cfg.values.inspection_date_final,
            }
        );
        this.getNotifyGrid().setFilterProperty('inspection', cfg.values.inspection, 101, true);
    }

});
