
Ext._define('common.saci.Configuration', {
    extend: 'toolkit.widget.TabPanel',

    dataReload: function() {
        this._config = core.nullValue(this.config, {});

        Ext.Ajax.request({
            url: core.callAction('SACIConfiguration', 'read'),
            scope: this,
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success)
                    this.getFormPanel().getForm().setValues(rst.config);
            }
        });
    },

    saveConfiguration: function() {
        
        Ext.Ajax.request({
            url: core.callAction('SACIConfiguration', 'save'),
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
                        labelWidth: 275,
                        items: [
                            {
                                xtype: 'rest-autocompletefield',
                                name: 'documentType',
                                fieldLabel: 'Tipo de documento',
                                rest: 'edocs.protocolo.TipoDocumentoRestful',
                                width: 550,
                            }
                        ]
                    }
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

        Ext.applyIf(
            cfg,
            {
                title: 'Configurações',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [this.getFormPanel()],
            }
        );

        common.saci.Configuration.superclass.constructor.call(this, cfg);
        this.dataReload();
    }
});
