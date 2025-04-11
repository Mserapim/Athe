var storeCache = {};

Ext._define('corregedoria.inspection.inspection.sign.Window', {
    extend: 'Ext.Window',

    store: function(cfg) {
        if(!this._store) {
            this._store = Ext._create('Ext.data.Store', {
                    autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('INSPECTIONInspection', 'get_signs')
                    }),
                    baseParams: {
                        inspection_id: cfg.values.inspection_id,
                        inspection_general_bool: cfg.values.inspector_general_bool,
                        inspection_prosecutor_bool: cfg.values.inspector_prosecutor_bool,
                    },
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {type: "auto", name: "ig_sign_at"},
                            {type: "auto", name: "ig_dispatch"},
                            {type: "auto", name: "ip_sign_at"},
                            {type: "auto", name: "ip_dispatch"},
                        ]
                    })
                });
                storeCache = this._store;
                this._store.load({
                    'scope': this,
                    'callback': function() {
                        if (storeCache.data.items["0"]) {
                            this.getFormPanel().getForm().setValues({
                                ig_sign_at: storeCache.data.items["0"].data.ig_sign_at,
                                ig_dispatch: storeCache.data.items["0"].data.ig_dispatch,
                                ip_sign_at: storeCache.data.items["0"].data.ip_sign_at,
                                ip_dispatch: storeCache.data.items["0"].data.ip_dispatch,
                            });
                            if (cfg.values.inspector_general_bool) {
                                if (storeCache.data.items["0"].data.ig_sign_at) {
                                    Ext.getCmp('ig_sign_at').setVisible(true);
                                    Ext.getCmp('btn_assinar').disable();
                                    Ext.getCmp('btn_remover_assinature').enable();
                                } else {
                                    Ext.getCmp('ig_sign_at').setVisible(false);
                                    Ext.getCmp('btn_assinar').enable();
                                    Ext.getCmp('btn_remover_assinature').disable();
                                }
                            }
                            if (cfg.values.inspector_prosecutor_bool) {
                                if (storeCache.data.items["0"].data.ip_sign_at) {
                                    Ext.getCmp('ip_sign_at').setVisible(true);
                                    Ext.getCmp('btn_assinar').disable();
                                    Ext.getCmp('btn_remover_assinature').enable();
                                } else {
                                    Ext.getCmp('ip_sign_at').setVisible(false);
                                    Ext.getCmp('btn_assinar').enable();
                                    Ext.getCmp('btn_remover_assinature').disable();
                                }
                            }
                        }
                    }
                });
            }
            return this._store;
    },

    getFormPanel: function() {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'hidden',
                        name: 'employee',
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 125,
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
                                        columnWidth: 0.78,
                                        items: [
                                            {
                                                xtype:'fieldset',
                                                title: 'Inspeção/Correição',
                                                collapsible: false,
                                                collapsed: false,
                                                autoHeight:true,
                                                width: 905,
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
                                                                width: 1000,
                                                                style: {fontWeight: 'bold'},
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'form',
                                                        labelWidth: 198,
                                                        items: [
                                                            {
                                                                xtype: 'displayfield',
                                                                name: 'employee_name',
                                                                fieldLabel: 'Procurador/Promotor Responsável',
                                                                width: 1000,
                                                                style: {fontWeight: 'bold'},
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'form',
                                                        labelWidth: 198,
                                                        items: [
                                                            {
                                                                xtype: 'displayfield',
                                                                name: 'responsible',
                                                                fieldLabel: 'Procurador/Promotor Inspecionado',
                                                                width: 1000,
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
                                                                width: 1000,
                                                                style: {fontWeight: 'bold'},
                                                            },
                                                        ]
                                                    },
                                                ]
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        columnWidth: 0.22,
                                        items: [
                                            {
                                                xtype:'fieldset',
                                                title: 'Nota Final',
                                                collapsible: false,
                                                collapsed: false,
                                                labelWidth: 1,
                                                items: [
                                                    {
                                                        xtype: 'displayfield',
                                                        id: 'final_score',
                                                        name: 'final_score',
                                                        style: {textAlign: 'center', fontSize: '56px', fontWeight: 'bolder'},
                                                    },
                                                ]
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                id: 'panel_inspector_prosecutor',
                                autoHeight:true,
                                layout: 'form',
                                items: [
                                    {
                                        xtype:'fieldset',
                                        title: 'Promotor-corregedor',
                                        collapsible: false,
                                        collapsed: false,
                                        height:370,
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
                                                        columnWidth: 0.75,
                                                        labelWidth: 1,
                                                        items: [
                                                            {
                                                                xtype: 'displayfield',
                                                                id: 'inspector_prosecutor',
                                                                name: 'inspector_prosecutor',
                                                                style: {fontSize: '18px', fontWeight: 'bolder'},
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'form',
                                                        columnWidth: 0.25,
                                                        labelWidth: 80,
                                                        items: [
                                                            {
                                                                xtype: 'displayfield',
                                                                fieldLabel: 'Assinado em',
                                                                id: 'ip_sign_at',
                                                                name: 'ip_sign_at',
                                                                style: {fontSize: '18px', fontWeight: 'bolder'},
                                                            },
                                                        ]
                                                    },
                                                ]
                                            },
                                            {
                                                xtype:'panel',
                                                autoHeight:true,
                                                layout: 'form',
                                                labelWidth: 60,
                                                items: [
                                                    {
                                                        xtype: "ckeditor",
                                                        fieldLabel: 'Despacho',
                                                        name: 'ip_dispatch',
                                                        submit: true,
                                                        height: 235,
                                                        startupFocus: false,
                                                        toolbarGroups: [
                                                            {name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ]},
                                                            {name: 'clipboard'},
                                                        ],
                                                    },
                                                ]
                                            },
                                        ]
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                id: 'panel_inspector_general',
                                autoHeight:true,
                                layout: 'form',
                                items: [
                                    {
                                        xtype:'fieldset',
                                        title: 'Corregedor-geral',
                                        collapsible: false,
                                        collapsed: false,
                                        height:370,
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
                                                        columnWidth: 0.75,
                                                        labelWidth: 1,
                                                        items: [
                                                            {
                                                                xtype: 'displayfield',
                                                                id: 'inspector_general',
                                                                name: 'inspector_general',
                                                                style: {fontSize: '18px', fontWeight: 'bolder'},
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'form',
                                                        columnWidth: 0.25,
                                                        labelWidth: 80,
                                                        items: [
                                                            {
                                                                xtype: 'displayfield',
                                                                fieldLabel: 'Assinado em',
                                                                id: 'ig_sign_at',
                                                                name: 'ig_sign_at',
                                                                style: {fontSize: '18px', fontWeight: 'bolder'},
                                                            },
                                                        ]
                                                    },
                                                ]
                                            },
                                            {
                                                xtype:'panel',
                                                autoHeight:true,
                                                layout: 'form',
                                                labelWidth: 60,
                                                items: [
                                                    {
                                                        xtype: "ckeditor",
                                                        fieldLabel: 'Despacho',
                                                        name: 'ig_dispatch',
                                                        submit: true,
                                                        height: 235,
                                                        startupFocus: false,
                                                        toolbarGroups: [
                                                            {name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ]},
                                                            {name: 'clipboard'},
                                                        ],
                                                    },
                                                ]
                                            },

                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                ]
            });
        }
        return this._formPanel;
    },

    sign: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        values.inspection_id = cfg.values.inspection_id;
        values.inspector_general_bool = cfg.values.inspector_general_bool;
        values.inspector_prosecutor_bool = cfg.values.inspector_prosecutor_bool;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Assinando inspeção...'});
        Ext.Msg.show({
            title: 'Assinar Inspeção/Correição',
            msg: 'Tem certeza que deseja assinar inspeção?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if(btn=='no') return;
                mask.show();
                Ext.Ajax.request({
                    scope: this,
                    url: core.callAction('INSPECTIONInspection', 'saveSign'),
                    callback: function() {
                        mask.hide();
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);
                        if (rst.success == true) {
                            Ext.Msg.show({
                                title: 'Assinar Inspeção/Correição',
                                msg: rst.message,
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK
                            });
                            core.invokeCallback((this.callback || {}).success);
                            cfg.values.gridInspection.getStore().reload();
                            this.close();
                        } else {
                            Ext.Msg.show({
                                title: 'Assinar Inspeção/Correição',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    failure: function(request) {
                        var rst = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            title: 'Assinar Inspeção/Correição',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    },
                    params: values,
                });
            }
        });
    },

    remove_sign: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        values.inspection_id = cfg.values.inspection_id;
        values.inspector_general_bool = cfg.values.inspector_general_bool;
        values.inspector_prosecutor_bool = cfg.values.inspector_prosecutor_bool;
        console.log(values);
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Removendo assinatura da inspeção...'});
        Ext.Msg.show({
            title: 'Remover assinatura da Inspeção/Correição',
            msg: 'Tem certeza que deseja remover a assinatura da inspeção?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if(btn=='no') return;
                mask.show();
                Ext.Ajax.request({
                    scope: this,
                    url: core.callAction('INSPECTIONInspection', 'removeSign'),
                    callback: function() {
                        mask.hide();
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);
                        if (rst.success == true) {
                            Ext.Msg.show({
                                title: 'Remover assinatura da Inspeção/Correição',
                                msg: rst.message,
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK
                            });
                            core.invokeCallback((this.callback || {}).success);
                            cfg.values.gridInspection.getStore().reload();
                            this.close();
                        } else {
                            Ext.Msg.show({
                                title: 'Remover assinatura da Inspeção/Correição',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    failure: function(request) {
                        var rst = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            title: 'Remover assinatura da Inspeção/Correição',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    },
                    params: values,
                });
            }
        });
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    id: 'btn_assinar',
                    text: '<b>Assinar</b>',
                    scope: this,
                    handler: function() {
                        this.sign(cfg);
                    }
                },
                {
                    id: 'btn_remover_assinature',
                    text: 'Remover assinatura',
                    scope: this,
                    handler: function() {
                        this.remove_sign(cfg);
                    }
                },
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
            title: 'Assinar Inspeção',
            width: 1200,
            height: 600,
            modal: true,
        });
        Ext.apply(cfg, {
            ds: this.store(cfg),
            items: [
                this.getFormPanel(cfg),
            ],
            buttons: this.getButtons(cfg),
        });
        corregedoria.inspection.inspection.sign.Window.superclass.constructor.call(this, cfg);
        console.log(cfg.values);
        this.getFormPanel().getForm().setValues(
            {
                employee_name: cfg.values.employee_name,
                responsible: cfg.values.responsible,
                execution_organ: cfg.values.execution_organ,
                inspection_date: cfg.values.inspection_date_initial + ' à ' + cfg.values.inspection_date_final,
                final_score: cfg.values.final_score ? cfg.values.final_score : 0,
                inspector_general: cfg.values.inspector_general,
                inspector_general_id: cfg.values.inspector_general_id,
                inspector_prosecutor: cfg.values.inspector_prosecutor,
                inspector_prosecutor_id: cfg.values.inspector_prosecutor_id,
                employee: cfg.values.employee,
            }
        );
        Ext.getCmp('panel_inspector_prosecutor').setVisible(cfg.values.inspector_prosecutor_bool);
        Ext.getCmp('panel_inspector_general').setVisible(cfg.values.inspector_general_bool);
    }

});
