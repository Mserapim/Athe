/**
 *
 **/
Ext._define('cif.referenceperiod.ConfigurationManage', {
    extend: 'toolkit.widget.TabPanel',

    autoCreateFor: function(value, persist) {
        persist = core.nullValue(persist, true);

        if(value !== undefined) {
            // this.getToTipodocumentoGrid().setFilterProperty('pk__in', value, 1000);
            // this.getFromTipodocumentoGrid().setFilterProperty('pk__in', value, -1000);

            this._autoCreateFor = value;

            if(persist) {
                Ext.Ajax.request({
                    url: core.callAction('CifConfiguration', 'write'),
                    params: {
                        property: 'autoCreateFor',
                        value: Ext.encode(this._autoCreateFor)
                    }
                });
            }
        }

        return this._autoCreateFor;
    },

    dataReload: function() {
        this._config = core.nullValue(this.config, {});

        Ext.Ajax.request({
            url: core.callAction('CifConfiguration', 'read'),
            scope: this,
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success) {
                    this.autoCreateFor(
                        rst.config.autoCreateFor,
                        false
                    );

                    this.getFormPanel().getForm().setValues(rst.config);
                }
            }
        });
    },

    saveConfiguration: function() {
        var values =

        Ext.Ajax.request({
            url: core.callAction('CifConfiguration', 'save'),
            scope: this,
            params: this.getFormPanel().getForm().getValues(),
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                var message, tipo;

                if(rst.success) {
                    message = 'Configurações persistidas com sucesso';
                    tipo = Ext.Msg.INFO;
                }
                else {
                    tipo = Ext.Msg.ERROR;
                    message = rst.message;
                }

                Ext.Msg.show({
                    title: 'Gravando configurações',
                    icon: tipo,
                    buttons: Ext.Msg.OK,
                    msg: message
                });
            }
        });
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                autoScroll: true,
                region: 'center',
                padding: '15',
                items: [
                    {
                        collapsible: true,
                        xtype: 'fieldset',
                        title: 'Gestor de Prazos para Preenchimento das informações',
                        layout: 'form',
                        labelWidth: 265,
                        items: [
                            {
                                allowBlank: true, 
                                width:250,
                                fieldLabel: "Data Limite para preenchimento de Docência", 
                                name: "deadline_teaching", 
                                xtype: "datefield"
                            },
                            {
                                allowBlank: true, 
                                width:250,
                                fieldLabel: "Data Limite para preenchimento de Endereço", 
                                name: "deadline_address", 
                                xtype: "datefield"
                            }, 
                            {
                                allowBlank: true, 
                                width:250,
                                fieldLabel: "Data Limite para preenchimento de Bens e Valores", 
                                name: "deadline_property", 
                                xtype: "datefield"
                            }, 
                            {
                                allowBlank: true, 
                                width:250,
                                fieldLabel: "Data Limite para preenchimento de Dívida Ônus Reais", 
                                name: "deadline_debtsencumbrances", 
                                xtype: "datefield"
                            }, 
                        ]
                    },
                ],
                buttons: [
                    {
                        text: 'Salvar',
                        scope: this,
                        handler: this.saveConfiguration
                    },
                    {
                        text: 'Restaurar',
                        scope: this,
                        handler: this.dataReload
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        this._values = {};

        Ext.applyIf(
            cfg,
            {
                title: 'Configurações'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [this.getFormPanel()],
            }
        );


        // this.callParent([cfg]);
        cif.referenceperiod.ConfigurationManage.superclass.constructor.call(this, cfg);
        this.dataReload();
    }
});
