/**
 *
 **/
Ext._define('adm.patrimonio.movimento.RestfulWindow', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.movimento.Restful',

    width: 1000,

    focusField: 'origem',

    getSourceField: function(cfg) {
        if (!this._sourceField) {
            this._sourceField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Origem dos Bens',
                allowBlank: true,
                rest: 'adm.patrimonio.localizacao.Restful',
                name: 'origem',
                anchor: '98%',
                preFilter: [
                    {property: 'ativo', value: 'true', stage: 1}
                ]
            });

            this._sourceField.getButton().disable();
        }

        return this._sourceField;
    },

    getDestinyField: function(cfg) {
        if (!this._destinyField) {
            this._destinyField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Destino dos Bens',
                allowBlank: true,
                rest: 'adm.patrimonio.localizacao.Restful',
                name: 'destino',
                anchor: '100%',
                preFilter: [
                    {property: 'ativo', value: true, stage: 100}
                ]
            });

            this._destinyField.getButton().disable();
        }

        return this._destinyField;
    },

    getInfoPanel: function() {
        if(!this._infoPanel)
            this._infoPanel = Ext._create('Ext.Panel', {
                layout: 'form',
                frame: true,
                border: false,
                title: 'Geral',
                items: [
                    {
                        xtype: 'displayfield',
                        name: 'identificacao',
                        fieldLabel: 'Indentificação',
                        value: 'Sem Indentificação'
                    },
                    {
                        fieldLabel: 'Estado',
                        xtype: 'displayfield',
                        name: 'status_display',
                        value: 'Criando'
                    },
                    {
                        title: 'Partes',
                        xtype: 'fieldset',
                        collapsible: true,
                        labelAlign: 'top',
                        items: [
                            {
                                layout: 'column',
                                labelAlign: 'top',
                                items: [
                                    {
                                        columnWidth: '0.5',
                                        layout: 'form',
                                        items: this.getSourceField()
                                    },
                                    {
                                        columnWidth: '0.5',
                                        layout: 'form',
                                        items: this.getDestinyField()
                                    }
                                ]
                            },

                            {
                                layout: 'column',
                                labelAlign: 'top',
                                items:
                                    {
                                        columnWidth: '1.0',
                                        layout: 'form',
                                        items:
                                        {
                                            xtype: 'rest-autocompletefield',
                                            rest: 'rh.employee.Restful',
                                            fieldLabel: 'Responsável',
                                            name: 'responsavel_destino',
                                            anchor: '100%'
                                        }
                                    }
                            }
                        ]
                    },
                    {
                        title: 'Responsáveis',
                        xtype: 'fieldset',
                        collapsible: true,
                        layout: 'hbox',
                        anchor: '100%',
                        defaults: {
                            labelAlign: 'top',
                            border: true,
                            flex: 1.0
                        },
                        items: [
                            {
                                xtype: 'panel',
                                layout: 'form',
                                items: {
                                    xtype: 'displayfield',
                                    hideLabel: true,
                                    name: 'assinatura_entrega'
                                }
                            },
                            {
                                xtype: 'panel',
                                layout: 'form',
                                items: {
                                    xtype: 'displayfield',
                                    hideLabel: true,
                                    name: 'assinatura_recebimento'
                                }
                            },
                            {
                                xtype: 'panel',
                                layout: 'form',
                                items: {
                                    xtype: 'displayfield',
                                    hideLabel: true,
                                    name: 'assinatura_patrimonio'
                                }
                            }
                        ]
                    }
                ]
            });

        return this._infoPanel;
    },

    getMovePanel: function() {
        if(!this._movePanel)
            this._movePanel = Ext._create('adm.patrimonio.movimento.LogStatusManage', {
                title: 'Mudanças de Estado'
            });

        return this._movePanel;
    },

    getDocumentoPanel: function() {
        if(!this._documentoPanel)
            this._documentoPanel = Ext._create('adm.patrimonio.DocumentoGrid', {
                title: 'Documentos'
            });

        return this._documentoPanel;
    },

    getNotificationPanel: function() {
        if (!this._notificationPanel) {
            this._notificationPanel = Ext._create('adm.patrimony.notification.Grid', {
                title: 'Notificação'
            });
        }

        return this._notificationPanel;
    },

    _observe: function() {
        var grid;

        if(this.oId) {
            grid = this.getMovePanel().getGridPanel();
            grid.enable();
            grid.setParam('movimento', this.oId);
            grid.setFilterProperty('movimento', this.oId);

            grid = this.getDocumentoPanel();
            grid.enable();
            grid.setParam('documentos_de_movimentacao', this.oId);
            grid.setFilterProperty('documentos_de_movimentacao', this.oId);

            grid = this.getNotificationPanel();
            grid.enable();
            grid.setParam('assets_movement', this.oId);
            grid.setFilterProperty('assets_movement', this.oId);
            grid.defaultValues({
                assets_movement_unicode: this.values.unicode,
            });
        }
        else {
            this.getMovePanel().disable();
            this.getDocumentoPanel().disable();
            this.getNotificationPanel().disable();
        }
    },

    reloadNotificationGrid: function () {
        this.getNotificationPanel().getStore().reload();
    },

    getTabPanel: function() {
        if (!this._tabPanel) {
            this._tabPanel = Ext._create('Ext.TabPanel', {
                height: 400,
                border: false,
                activeTab: 0,
                items: [
                    this.getInfoPanel(),
                    this.getMovePanel(),
                    this.getDocumentoPanel(),
                    this.getNotificationPanel()
                ],
                listeners: {
                    scope: this,
                    render: function(container) {
                        core.RemoteObserver.on('edoc-load-boxes', {
                            scope: this,
                            fn: this.reloadNotificationGrid
                        });
                    },
                    destroy: function () {
                        core.RemoteObserver.un('edoc-load-boxes', this.reloadNotificationGrid);
                    }
                }
            });
        }

        return this._tabPanel;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: this.getTabPanel()
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        adm.patrimonio.movimento.RestfulWindow.superclass.constructor.call(this, cfg);
        this._observe();
    }
});
