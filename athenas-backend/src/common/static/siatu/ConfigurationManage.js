Ext._define('common.siatu.ConfigurationManage', {
    extend: 'toolkit.widget.TabPanel',

    autoCreateFor: function(value, persist) {
        persist = core.nullValue(persist, true);

        if(value !== undefined) {
            // this.getToTipodocumentoGrid().setFilterProperty('pk__in', value, 1000);
            // this.getFromTipodocumentoGrid().setFilterProperty('pk__in', value, -1000);

            this._autoCreateFor = value;

            if(persist) {
                Ext.Ajax.request({
                    url: core.callAction('SiatuConfiguracao', 'write'),
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
            url: core.callAction('SiatuConfiguracao', 'read'),
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
            url: core.callAction('SiatuConfiguracao', 'save'),
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
                        title: 'Informações Gerais',
                        layout: 'form',
                        labelWidth: 265,
                        items: [
                            {
                                fieldLabel: 'Quantidade Máxima de dias para Avaliação do Chamado',
                                xtype: 'numberfield',
                                allowDecimal: false,
                                width: 150,
                                style: 'text-align: right',
                                name: 'max_dias_avaliacao',
                                minValue: 0,
                                allowNegative: false
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
        common.siatu.ConfigurationManage.superclass.constructor.call(this, cfg);
        this.dataReload();
    }
});
