
Ext._define('planning.hiring.configuration.MinuteConfiguration', {
    extend: 'toolkit.widget.TabPanel',

    dataReload: function() {
        this._config = core.nullValue(this.config, {});

        Ext.Ajax.request({
            url: core.callAction('PHMMinuteConfiguration', 'dataReload'),
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
            url: core.callAction('PHMMinuteConfiguration', 'save'),
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
                    url: core.callAction('PHMMinuteConfiguration', 'write'),
                    params: {
                        property: 'jobPosition',
                        value: Ext.encode(this._updatePanels)
                    }
                });
            }
        }

        return this._updatePanels;
    },

    addJobPosition: function(selected) {
        selected = core.nullValue(
            selected,
            this.getAvailableJobPositionGrid().getSelectionModel().getSelections().map(
                function(data) {
                    return data.get('pk');
                }
            )
        );

        if(selected.length > 0) {
            selected = selected.concat(this.updatePanels());
            this.updatePanels(selected);
        }
        else
            Ext.Msg.show({
                'title': 'Adicionando',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Primeiro selecione os itens a serem adicionados.'
            });
    },

    addAllJobPosition: function() {
        var selected = [];

        this.getAvailableJobPositionGrid().getStore().each(
            function(data) {
                selected.push(data.get('pk'));
            }
        );

        this.addJobPosition(selected);
    },

    removeJobPosition: function(selected) {
        selected = core.nullValue(
            selected,
            this.getSelectedJobPositionGrid().getSelectionModel().getSelections().map(
                function(data) {
                    return data.get('pk');
                }
            )
        );

        if(selected.length > 0) {
            var value = this.updatePanels();
            selected.map(function(pk) { value.remove(pk); });
            this.updatePanels(value);
        }
        else
            Ext.Msg.show({
                'title': 'Removendo',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Primeiro selecione os itens a serem removidos.'
            });
    },

    removeAllJobPosition: function() {
        var selected = [];

        this.getSelectedJobPositionGrid().getStore().each(
            function(data) {
                selected.push(data.get('pk'));
            }
        );

        this.removeJobPosition(selected);
    },

    getAvailableJobPositionGrid: function() {
        var self = this;

        if(!this._availableJobPosition) {
            this._availableJobPosition = Ext._create('rh.jobposition.Grid', {
                title: 'Disponíveis',
                border: true,
                flex: 1,
                doubleClickHandler: function() { self.addJobPosition(); },
                gridAutoLoad: false,
                columnAction: false,
                configOrderToolBar: ['search'],
                hideColumns: [
                    'ativo',
                    'unidade_administrativa_unicode',
                    'lotacao_responsavel_unicode',
                    'chefia',
                    'substituivel',
                    'tipo_lei_cargo_display',
                    'indicativo_display',
                    'codigo',
                    'acumulavel'
                ],
            });

            // this._availableJobPosition.setFilterProperty('pk__in', core.nullValue(this._values.updatePanels, []), -1000, false);
            this._availableJobPosition.setFilterProperty('ativo', true, 1001, false);
        }

        return this._availableJobPosition;
    },

    getSelectedJobPositionGrid: function() {
        var self = this;

        if(!this._selectedJobPosition) {
            this._selectedJobPosition = Ext._create('rh.jobposition.Grid', {
                title: 'Selecionados',
                border: true,
                flex: 1,
                doubleClickHandler: function() { self.removeJobPosition(); },
                gridAutoLoad: false,
                columnAction: false,
                configOrderToolBar: ['search'],
                hideColumns: [
                    'ativo',
                    'unidade_administrativa_unicode',
                    'lotacao_responsavel_unicode',
                    'chefia',
                    'substituivel',
                    'tipo_lei_cargo_display',
                    'indicativo_display',
                    'codigo',
                    'acumulavel'
                ],
            });

            // this._selectedJobPosition.setFilterProperty('pk__in', core.nullValue(this._values.updatePanels, []), 1000, false);
        }

        return this._selectedJobPosition;
    },

    getJobPositionPanel: function() {
        if(!this._fieldsetBasic)
            this._fieldsetBasic = Ext._create('Ext.form.FieldSet', {
                title: 'Cargos',
                collapsible: true,
                layout: {
                    type: 'hbox',
                    align: 'stretchmax',
                    padding: '0 0 6 0'
                },
                items: [
                    this.getAvailableJobPositionGrid(),
                    {
                        width: 35,
                        height: 350,
                        xtype: 'container',
                        frame: true,
                        layout: {
                            type: 'vbox',
                            align: 'stretchmax',
                            padding: '6'
                        },
                        items: [
                            {
                                xtype: 'container',
                                flex: 1
                            },
                            {
                                xtype: 'container',
                                defaults: {
                                    xtype: 'button',
                                    width: 24,
                                    height: 24,
                                    style: {
                                        marginBottom: '5px'
                                    }
                                },
                                items: [
                                    {
                                        iconCls: 'icon-core icon-core-add-all',
                                        scope: this,
                                        handler: function() {this.addAllJobPosition(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-add-selected',
                                        scope: this,
                                        handler: function() {this.addJobPosition(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-remove-selected',
                                        scope: this,
                                        handler: function() {this.removeJobPosition(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-remove-all',
                                        scope: this,
                                        handler: function() {this.removeAllJobPosition(); }
                                    }
                                ]
                            },
                            {
                                xtype: 'container',
                                flex: 1
                            }
                        ]
                    },
                    this.getSelectedJobPositionGrid()
                ]
            });

        return this._fieldsetBasic;
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
                        collapsible: true,
                        xtype: 'fieldset',
                        title: 'Quem limita o n° de Adesões por Ata',
                        layout: 'form',
                        labelWidth: 275,
                        items: [
                            {
                                xtype: 'rest-autocompletefield',
                                name: 'management_organ',
                                fieldLabel: 'Órgão Gerenciador',
                                rest: 'rh.generalorgan.Restful',
                                width: 550,
                            },
                        ]
                    },
                    this.getJobPositionPanel()
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
                title: 'Configurações - Gestor de Ata',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getFormPanel(),
            }
        );

        planning.hiring.configuration.MinuteConfiguration.superclass.constructor.call(this, cfg);
        this.dataReload();
    }
});
