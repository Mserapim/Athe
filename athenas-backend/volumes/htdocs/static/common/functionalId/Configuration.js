
Ext._define('common.functionalId.Configuration', {
    extend: 'toolkit.widget.TabPanel',

    dataReload: function() {
        this._config = core.nullValue(this.config, {});

        Ext.Ajax.request({
            url: core.callAction('FIdFunctionalIdConfiguration', 'dataReload'),
            scope: this,
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success) {
                    this.updatePanels(
                        rst.config.jobPosition,
                        false
                    );

                    this.getFormPanel().getForm().setValues(rst.config);
                }
            }
        });
    },

    saveConfiguration: function() {
        Ext.Ajax.request({
            url: core.callAction('FIdFunctionalIdConfiguration', 'save'),
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

    updatePanels: function(value, persist) {
        persist = core.nullValue(persist, true);

        if(value !== undefined) {
            this.getSelectedJobPositionGrid().setFilterProperty('pk__in', value, 1000);
            this.getAvailableJobPositionGrid().setFilterProperty('pk__in', value, -1000);

            this._updatePanels = value;

            if(persist) {
                Ext.Ajax.request({
                    url: core.callAction('FIdFunctionalIdConfiguration', 'write'),
                    params: {
                        property: 'jobPosition',
                        value: Ext.encode(this._updatePanels)
                    }
                });
            }
        }

        return this._updatePanels;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                autoScroll: true,
                region: 'center',
                labelAlign: 'top',
                padding: '10',
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        name: 'signatory_job_position',
                        fieldLabel: 'Cargo do signatário',
                        rest: 'rh.jobposition.Restful',
                        width: 550,
                        gridConfig: {
                            columnAction: false,
                            allowCreate: false,
                            allowUpdate: false,
                            allowRemove: false,
                            configOrderToolBar: ['search', '->'],
                            hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                            onlyColumns: ['ativo', 'unicode', 'codigo'],
                        }
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

        this._values = {};

        Ext.applyIf(
            cfg,
            {
                title: 'Configurações - Gestor de Identidade Funcional',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getFormPanel(),
            }
        );

        common.functionalId.Configuration.superclass.constructor.call(this, cfg);
        this.dataReload();
    }
});
