Ext._define('raf.Configuration', {
    extend: 'toolkit.widget.TabPanel',

    dataReload: function() {
        this._config = core.nullValue(this.config, {});

        Ext.Ajax.request({
            url: core.callAction('RAFConfiguration', 'read'),
            scope: this,
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success)
                    this.getFormPanel().getForm().setValues(rst.config);
            }
        });
    },

    saveConfiguration: function() {
        var values =

        Ext.Ajax.request({
            url: core.callAction('RAFConfiguration', 'save'),
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

    getSpecialOrgan: function() {
        if(!this._specialOrgan) {
            this._specialOrgan = Ext._create('raf.specialorgan.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 450,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['download', ],
                doubleClickHandler: function() { },
            });
        }
        return this._specialOrgan;
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
                            },
                        ]
                    },
                    {
                        collapsible: true,
                        xtype: 'fieldset',
                        title: 'Local utilizado nas respostas',
                        layout: 'form',
                        labelWidth: 275,
                        items: [
                            {
                                xtype: 'rest-autocompletefield',
                                name: 'location',
                                fieldLabel: 'Lotação',
                                rest: 'rh.workplace.Restful',
                                width: 550,
                            },
                        ]
                    },
                    {
                        collapsible: true,
                        xtype: 'fieldset',
                        title: 'Ajustes',
                        layout: 'form',
                        labelWidth: 275,
                        items: [
                            {
                                xtype: 'choicefield',
                                fieldLabel: 'Ajustes em atividades',
                                hiddenName: 'activities_maintenance',
                                width: 465,
                                choiceId: 'raf.ACTIVITIES_MAINTANANCE',
                            },
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Órgãos especiais',
                        layout: 'form',
                        collapsible: true,
                        collapsed: false,
                        items: [
                            this.getSpecialOrgan(),
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

        raf.Configuration.superclass.constructor.call(this, cfg);
        this.dataReload();
    }
});
