var storeCache = {};

Ext._define('corregedoria.prontuary.generaldata.Window', {
    extend: 'Ext.Window',

    store: function(cfg) {
        if(!this._store) {
            this._store = Ext._create('Ext.data.Store', {
                    autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('PRONTUARYProntuary', 'get_generaldata')
                    }),
                    baseParams: {
                        prontuary: cfg.values.prontuary,
                    },
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {type: "auto", name: "vitality_date"},
                            {type: "auto", name: "vitality_doc"},
                            {type: "auto", name: "seniority_position"},
                            {type: "auto", name: "ordinance_seniority_position"},
                            {type: "auto", name: "public_service_time"},
                        ]
                    })
                });
                storeCache = this._store;
                this._store.load({
                    'scope': this,
                    'callback': function() {
                        if (storeCache.data.items["0"]) {
                            this.getFormPanel().getForm().setValues({
                                vitality_date: storeCache.data.items["0"].data.vitality_date,
                                vitality_doc: storeCache.data.items["0"].data.vitality_doc,
                                seniority_position: storeCache.data.items["0"].data.seniority_position,
                                ordinance_seniority_position: storeCache.data.items["0"].data.ordinance_seniority_position,
                                public_service_time: storeCache.data.items["0"].data.public_service_time,
                            });
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
                        xtype:'fieldset',
                        title: 'Vitaliciamento',
                        hideLabel: true,
                        autoHeight: true,
                        collapsible: false,
                        width: 570,
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                labelWidth: 35,
                                // columnWidth: 0.2,
                                layout: 'form',
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'Data',
                                        width: 100,
                                        name: 'vitality_date',
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                labelWidth: 70,
                                // columnWidth: 0.8,
                                layout: 'form',
                                items: [
                                    {
                                        xtype: 'textfield',
                                        fieldLabel: 'Documento',
                                        name: 'vitality_doc',
                                        width: 470,

                                    }
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'fieldset',
                        title: 'Informações para Desempate',
                        hideLabel: true,
                        autoHeight: true,
                        collapsible: false,
                        width: 570,
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'column',
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        columnWidth: 1,
                                        layout: 'column',
                                        items: [
                                            {
                                                xtype:'panel',
                                                autoHeight:true,
                                                labelWidth: 195,
                                                columnWidth: 0.5,
                                                layout: 'form',
                                                items: [
                                                    {
                                                        xtype: 'textfield',
                                                        fieldLabel: 'Posição no Quadro de Antiguidade',
                                                        name: 'seniority_position',
                                                        width: 50,

                                                    },
                                                ]
                                            },
                                            {
                                                xtype:'panel',
                                                autoHeight:true,
                                                labelWidth: 50,
                                                columnWidth: 0.5,
                                                layout: 'form',
                                                items: [
                                                    {
                                                        xtype: 'textfield',
                                                        fieldLabel: 'Portaria',
                                                        name: 'ordinance_seniority_position',
                                                        width: 210,

                                                    },
                                                ]
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        labelWidth: 145,
                                        columnWidth: 1,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'textfield',
                                                fieldLabel: 'Tempo de Serviço Público',
                                                name: 'public_service_time',
                                                width: 200,

                                            }
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

    save: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        values.prontuary = cfg.values.prontuary;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Escrevendo no Prontuário Individual...'});
        Ext.Msg.show({
            title: 'Dados Gerais - Prontuário Individual',
            msg: 'Tem certeza que deseja salvar Dados Gerais - Prontuário Individual?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if(btn=='no') return;
                mask.show();
                Ext.Ajax.request({
                    scope: this,
                    url: core.callAction('PRONTUARYProntuary', 'saveGeneralData'),
                    callback: function() {
                        mask.hide();
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);
                        if (rst.success == true) {
                            Ext.Msg.show({
                                title: 'Dados Gerais - Prontuário Individual',
                                msg: rst.message,
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK
                            });
                            this.close();
                        } else {
                            Ext.Msg.show({
                                title: 'Dados Gerais - Prontuário Individual',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    failure: function(request) {
                        var rst = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            title: 'Dados Gerais - Prontuário Individual',
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
                    id: 'btn_save',
                    text: '<b>Salvar</b>',
                    scope: this,
                    handler: function() {
                        this.save(cfg);
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
            title: 'Dados Gerais - Prontuário Individual',
            width: 600,
            height: 275,
            modal: true,
        });
        Ext.apply(cfg, {
            ds: this.store(cfg),
            items: [
                this.getFormPanel(cfg),
            ],
            buttons: this.getButtons(cfg),
        });
        corregedoria.prontuary.generaldata.Window.superclass.constructor.call(this, cfg);
    }

});
