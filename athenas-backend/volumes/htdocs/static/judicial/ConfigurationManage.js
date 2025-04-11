/**
 *
 **/
Ext._define('judicial.ConfigurationManage', {
    extend: 'toolkit.widget.TabPanel',

    getFromTriageCenterGrid: function() {
        var self = this;

        if(!this._fromTriageCenter) {
            this._fromTriageCenter = Ext._create('rh.workplace.Grid', {
                title: 'Disponível',
                border: true,
                flex: 1,
                doubleClickHandler: function() { self.addTriageCenter(); },
                gridAutoLoad: false,
                columnAction: false,
                configOrderToolBar: ['search', '->', 'download'],
                onlyColumns: ['ativo', 'unicode', 'sigla']
            });

            // this._fromTriageCenter.setFilterProperty('pk__in', core.nullValue(this._values.triageCenter, []), -1000);
        }

        return this._fromTriageCenter;
    },

    getToTriageCenterGrid: function() {
        var self = this;

        if(!this._toTriageCenter) {
            this._toTriageCenter = Ext._create('rh.workplace.Grid', {
                title: 'Selecionado',
                border: true,
                flex: 1,
                doubleClickHandler: function() { self.removeTriageCenter(); },
                gridAutoLoad: false,
                columnAction: false,
                configOrderToolBar: ['search', '->', 'download'],
                onlyColumns: ['ativo', 'unicode', 'sigla']
            });

            // this._toTriageCenter.setFilterProperty('pk__in', core.nullValue(this._values.triageCenter, []), 1000);
        }

        return this._toTriageCenter;
    },

    getFieldSetTriageCenter: function() {
        if(!this._fieldsetTriageCenter)
            this._fieldsetTriageCenter = Ext._create('Ext.form.FieldSet', {
                title: 'Centrais Auxiliares de Triagem',
                collapsible: true,
                layout: {
                    type: 'hbox',
                    align: 'stretchmax',
                    padding: '0 0 6 0'
                },
                items: [
                    this.getFromTriageCenterGrid(),
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
                                        handler: function() {this.addAllTriageCenter(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-add-selected',
                                        scope: this,
                                        handler: function() {this.addTriageCenter(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-remove-selected',
                                        scope: this,
                                        handler: function() {this.removeTriageCenter(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-remove-all',
                                        scope: this,
                                        handler: function() {this.removeAllTriageCenter(); }
                                    }
                                ]
                            },
                            {
                                xtype: 'container',
                                flex: 1
                            }
                        ]
                    },
                    this.getToTriageCenterGrid()
                ]
            });

        return this._fieldsetTriageCenter;
    },

    removeAllTriageCenter: function() {
        var selected = [];

        this.getToTriageCenterGrid().getStore().each(
            function(data) {
                selected.push(data.get('pk'));
            }
        );

        this.removeTriageCenter(selected);
    },

    removeTriageCenter: function(selected) {
        selected = core.nullValue(
            selected,
            this.getToTriageCenterGrid().getSelectionModel().getSelections().map(
                function(data) {
                    return data.get('pk');
                }
            )
        );

        if(selected.length > 0) {
            var value = this.triageCenter();
            selected.map(function(pk) { value.remove(pk); });
            this.triageCenter(value);
        }
        else
            Ext.Msg.show({
                'title': 'Removendo',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Primeiro selecione os itens a serem removidos.'
            });
    },

    addAllTriageCenter: function() {
        var selected = [];

        this.getFromTriageCenterGrid().getStore().each(
            function(data) {
                selected.push(data.get('pk'));
            }
        );

        this.addTriageCenter(selected);
    },

    addTriageCenter: function(selected) {
        selected = core.nullValue(
            selected,
            this.getFromTriageCenterGrid().getSelectionModel().getSelections().map(
                function(data) {
                    return data.get('pk');
                }
            )
        );

        if(selected.length > 0) {
            selected = selected.concat(this.triageCenter());
            this.triageCenter(selected);
        }
        else
            Ext.Msg.show({
                'title': 'Adicionando',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Primeiro selecione os itens a serem adiconados.'
            });
    },

    triageCenter: function(value, persist) {
        persist = core.nullValue(persist, true);

        if(value !== undefined) {
            this.getFromTriageCenterGrid().setFilterProperty('pk__in', value, -1000, false);
            this.getFromTriageCenterGrid().setFilterProperty('habilita_protocolo', 'on', 1000);
            this.getToTriageCenterGrid().setFilterProperty('pk__in', value, 1000);

            this._triageCenter = value;

            if(persist) {
                Ext.Ajax.request({
                    url: core.callAction('EJudConfiguration', 'write'),
                    params: {
                        property: 'triageCenter',
                        value: Ext.encode(this._triageCenter)
                    }
                });
            }
        }

        return this._triageCenter;
    },

    getFromTipodocumentoGrid: function() {
        var self = this;

        if(!this._fromTipoDocumento) {
            this._fromTipoDocumento = Ext._create('edocs.protocolo.TipoDocumentoGrid', {
                title: 'Disponível',
                border: true,
                flex: 1,
                doubleClickHandler: function() { self.addAutoCreateFor(); },
                gridAutoLoad: false,
                columnAction: false,
                configOrderToolBar: ['search', '->', 'download']
            });

            // this._fromTipoDocumento.setFilterProperty('pk__in', core.nullValue(this._values.autoCreateFor, []), -1000);
        }

        return this._fromTipoDocumento;
    },

    getToTipodocumentoGrid: function() {
        var self = this;

        if(!this._toTipoDocumento) {
            this._toTipoDocumento = Ext._create('edocs.protocolo.TipoDocumentoGrid', {
                title: 'Selecionado',
                border: true,
                flex: 1,
                doubleClickHandler: function() { self.removeAutoCreateFor(); },
                gridAutoLoad: false,
                columnAction: false,
                configOrderToolBar: ['search', '->', 'download']
            });

            // this._toTipoDocumento.setFilterProperty('pk__in', core.nullValue(this._values.autoCreateFor, []), 1000);
        }

        return this._toTipoDocumento;
    },

    getFieldSetBasic: function() {
        if(!this._fieldsetBasic)
            this._fieldsetBasic = Ext._create('Ext.form.FieldSet', {
                title: 'Tipo de documento que se transforma em Notícia de Fato automáticamente',
                collapsible: true,
                layout: {
                    type: 'hbox',
                    align: 'stretchmax',
                    padding: '0 0 6 0'
                },
                items: [
                    this.getFromTipodocumentoGrid(),
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
                                        handler: function() {this.addAllAutoCreateFor(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-add-selected',
                                        scope: this,
                                        handler: function() {this.addAutoCreateFor(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-remove-selected',
                                        scope: this,
                                        handler: function() {this.removeAutoCreateFor(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-remove-all',
                                        scope: this,
                                        handler: function() {this.removeAllAutoCreateFor(); }
                                    }
                                ]
                            },
                            {
                                xtype: 'container',
                                flex: 1
                            }
                        ]
                    },
                    this.getToTipodocumentoGrid()
                ]
            });

        return this._fieldsetBasic;
    },

    removeAllAutoCreateFor: function() {
        var selected = [];

        this.getToTipodocumentoGrid().getStore().each(
            function(data) {
                selected.push(data.get('pk'));
            }
        );

        this.removeAutoCreateFor(selected);
    },

    removeAutoCreateFor: function(selected) {
        selected = core.nullValue(
            selected,
            this.getToTipodocumentoGrid().getSelectionModel().getSelections().map(
                function(data) {
                    return data.get('pk');
                }
            )
        );

        if(selected.length > 0) {
            var value = this.autoCreateFor();
            selected.map(function(pk) { value.remove(pk); });
            this.autoCreateFor(value);
        }
        else
            Ext.Msg.show({
                'title': 'Removendo',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Primeiro selecione os itens a serem removidos.'
            });
    },

    addAllAutoCreateFor: function() {
        var selected = [];

        this.getFromTipodocumentoGrid().getStore().each(
            function(data) {
                selected.push(data.get('pk'));
            }
        );

        this.addAutoCreateFor(selected);
    },

    addAutoCreateFor: function(selected) {
        selected = core.nullValue(
            selected,
            this.getFromTipodocumentoGrid().getSelectionModel().getSelections().map(
                function(data) {
                    return data.get('pk');
                }
            )
        );

        if(selected.length > 0) {
            selected = selected.concat(this.autoCreateFor());
            this.autoCreateFor(selected);
        }
        else
            Ext.Msg.show({
                'title': 'Adicionando',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Primeiro selecione os itens a serem adiconados.'
            });
    },

    autoCreateFor: function(value, persist) {
        persist = core.nullValue(persist, true);

        if(value !== undefined) {
            this.getToTipodocumentoGrid().setFilterProperty('pk__in', value, 1000);
            this.getFromTipodocumentoGrid().setFilterProperty('pk__in', value, -1000);

            this._autoCreateFor = value;

            if(persist) {
                Ext.Ajax.request({
                    url: core.callAction('EJudConfiguration', 'write'),
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
            url: core.callAction('EJudConfiguration', 'read'),
            scope: this,
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success) {
                    this.autoCreateFor(
                        rst.config.autoCreateFor,
                        false
                    );

                    this.triageCenter(
                        rst.config.triageCenter,
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
            url: core.callAction('EJudConfiguration', 'save'),
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

    getFieldSetCouncil: function() {
        if(!this._fieldSetCouncil)
            this._fieldSetCouncil = Ext._create('Ext.form.FieldSet', {
                title: 'Conselho Superior do Ministério Público',
                collapsible: true,
                collapsed: true,
                labelWidth: 265,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        name: 'presidentCouncil',
                        fieldLabel: 'Presidente do Conselho',
                        rest: 'rh.jobposition.Restful',
                        width: 550,
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        name: 'inspectorCouncil',
                        fieldLabel: 'Corregedor Geral',
                        rest: 'rh.jobposition.Restful',
                        width: 550,
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        name: 'electedCouncil',
                        fieldLabel: 'Conselheiros',
                        rest: 'rh.jobposition.Restful',
                        width: 550,
                    },
                    {
                        fieldLabel: 'Convocação de Entidades (prazo em dias)',
                        xtype: 'numberfield',
                        allowDecimal: false,
                        width: 90,
                        style: 'text-align: right',
                        name: 'deadlineConvocationNotice',
                        minValue: 0,
                        allowNegative: false
                    }
                ]
            });

        return this._fieldSetCouncil;
    },

    getFieldSetDilation: function() {
        if(!this._fieldSetDilation)
            this._fieldSetDilation = Ext._create('Ext.form.FieldSet', {
                title: 'Pedidos de dilação de prazo',
                collapsible: true,
                collapsed: true,
                labelWidth: 265,
                items: [
                    {
                        fieldLabel: 'Notícia de Fato',
                        xtype: 'numberfield',
                        allowDecimal: false,
                        width: 90,
                        style: 'text-align: right',
                        name: 'dilationMaxFactNews',
                        allowBlank: true,
                        minValue: 0,
                        allowNegative: false
                    },
                    {
                        fieldLabel: 'Notícia de Fato (Criminal)',
                        xtype: 'numberfield',
                        allowDecimal: false,
                        width: 90,
                        style: 'text-align: right',
                        name: 'dilationMaxCriminalFactNews',
                        allowBlank: true,
                        minValue: 0,
                        allowNegative: false
                    },
                    {
                        fieldLabel: 'Triagem',
                        xtype: 'numberfield',
                        allowDecimal: false,
                        width: 90,
                        style: 'text-align: right',
                        name: 'dilationMaxTriage',
                        allowBlank: true,
                        minValue: 0,
                        allowNegative: false
                    },
                    {
                        fieldLabel: 'Inquerito Civil',
                        xtype: 'numberfield',
                        allowDecimal: false,
                        width: 90,
                        style: 'text-align: right',
                        name: 'dilationMaxCivilInvestigation',
                        allowBlank: true,
                        minValue: 0,
                        allowNegative: false
                    },
                    {
                        fieldLabel: 'Procedimento Preparatório',
                        xtype: 'numberfield',
                        allowDecimal: false,
                        width: 90,
                        style: 'text-align: right',
                        name: 'dilationMaxPreparatoryProcedure',
                        allowBlank: true,
                        minValue: 0,
                        allowNegative: false
                    },
                    {
                        fieldLabel: 'P. Investigatório Criminal',
                        xtype: 'numberfield',
                        allowDecimal: false,
                        width: 90,
                        style: 'text-align: right',
                        name: 'dilationMaxPreparatoryCivilInvestigation',
                        allowBlank: true,
                        minValue: 0,
                        allowNegative: false
                    },
                    {
                        fieldLabel: 'Procedimento Administrativo',
                        xtype: 'numberfield',
                        allowDecimal: false,
                        width: 90,
                        style: 'text-align: right',
                        name: 'dilationMaxAdministrativeProcedure',
                        allowBlank: true,
                        minValue: 0,
                        allowNegative: false
                    },
                    {
                        fieldLabel: 'Carta Precatória',
                        xtype: 'numberfield',
                        allowDecimal: false,
                        width: 90,
                        style: 'text-align: right',
                        name: 'dilationRogatoryLetter',
                        allowBlank: true,
                        minValue: 0,
                        allowNegative: false
                    }
                ]
            });

        return this._fieldSetDilation;
    },

    getFieldSetDiligence: function() {
        if(!this._fieldSetDiligence)
            this._fieldSetDiligence = Ext._create('Ext.form.FieldSet', {
                title: 'Diligências',
                collapsible: true,
                collapsed: true,
                labelWidth: 265,
                items: [
                    {
                        fieldLabel: 'Quantidade Máxima de Tentativas de Entrega',
                        xtype: 'numberfield',
                        allowDecimal: false,
                        width: 150,
                        style: 'text-align: right',
                        name: 'deadlineDiligence',
                        minValue: 0,
                        allowNegative: false
                    },
                    {
                        xtype: 'combo',
                        lazyRender: true,
                        width: 150,
                        hiddenName: 'automatic_publication',
                        fieldLabel: 'Tipo de Publicação em Diário Oficial',
                        store: [
                            [1, 'MANUAL'],
                            [2, 'AUTOMÁTICO']
                        ],
                        allowBlank: false,
                        triggerAction: 'all',
                        value: 1,
                    },
                ]
            });

        return this._fieldSetDiligence;
    },

    getFieldSetPortaria: function() {
        if(!this._fieldSetPortaria)
            this._fieldSetPortaria = Ext._create('Ext.form.FieldSet', {
                title: 'Portaria de Instauração',
                collapsible: true,
                collapsed: true,
                labelWidth: 265,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        name: 'typeDocument',
                        fieldLabel: 'Documento de Comunicação',
                        rest: 'edocs.protocolo.TipoDocumentoRestful',
                        width: 550
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Documento de Publicação',
                        hiddenName: 'typePublication',
                        width: 550,
                        choiceId: 'rh.TIPO_DOCUMENTO'
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Veiculo de Publicação',
                        hiddenName: 'vehiclePublication',
                        width: 550,
                        choiceId: 'rh.VEICULO_PUBLICACAO'
                    }
                ]
            });

        return this._fieldSetPortaria;
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
                                name: 'officePresident',
                                fieldLabel: 'Gabinente do Procurador Geral',
                                rest: 'rh.workplace.Restful',
                                width: 550
                            },
                            {
                                xtype: 'rest-autocompletefield',
                                name: 'csmpLocation',
                                fieldLabel: 'Conselho Superior do MP',
                                rest: 'rh.workplace.Restful',
                                width: 550,
                                preFilter: [
                                    {property: 'habilita_protocolo', value: 'on', stage: 10}
                                ]
                            },
                            {
                                xtype: 'rest-autocompletefield',
                                name: 'mainTriageCenter',
                                fieldLabel: 'Central de Triagem Principal',
                                rest: 'rh.workplace.Restful',
                                width: 550,
                                preFilter: [
                                    {property: 'habilita_protocolo', value: 'on', stage: 10}
                                ]
                            },
                            {
                                xtype: 'rest-autocompletefield',
                                name: 'cjpLocation',
                                fieldLabel: 'Colegio de Procuradores',
                                rest: 'rh.workplace.Restful',
                                width: 550,
                                preFilter: [
                                    {property: 'habilita_protocolo', value: 'on', stage: 10}
                                ]
                            },
                            {
                                fieldLabel: 'Notícia de Fato (prazo em dias)',
                                xtype: 'numberfield',
                                allowDecimal: false,
                                width: 90,
                                style: 'text-align: right',
                                name: 'deadlineFactNews',
                                minValue: 0,
                                allowNegative: false
                            },
                            {
                                fieldLabel: 'Triagem (prazo em dias)',
                                xtype: 'numberfield',
                                allowDecimal: false,
                                width: 90,
                                style: 'text-align: right',
                                name: 'deadlineTriage',
                                minValue: 0,
                                allowNegative: false
                            },
                            {
                                fieldLabel: 'Inquerito Civil (prazo em dias)',
                                xtype: 'numberfield',
                                allowDecimal: false,
                                width: 90,
                                style: 'text-align: right',
                                name: 'deadlineCivilInvestigation',
                                minValue: 0,
                                allowNegative: false
                            },
                            {
                                fieldLabel: 'Procedimento Preparatório (prazo em dias)',
                                xtype: 'numberfield',
                                allowDecimal: false,
                                width: 90,
                                style: 'text-align: right',
                                name: 'deadlinePreparatoryProcedure',
                                minValue: 0,
                                allowNegative: false
                            },
                            {
                                fieldLabel: 'Procedimento Administrativo',
                                xtype: 'numberfield',
                                allowDecimal: false,
                                width: 90,
                                style: 'text-align: right',
                                name: 'deadlineAdministrativeProcedure',
                                minValue: 0,
                                allowNegative: false
                            },
                            {
                                fieldLabel: 'P. Investigatório Criminal (prazo em dias)',
                                xtype: 'numberfield',
                                allowDecimal: false,
                                width: 90,
                                style: 'text-align: right',
                                name: 'deadlinePreparatoryCivilInvestigation',
                                minValue: 0,
                                allowNegative: false
                            },
                            {
                                fieldLabel: 'Finalizar instauração de oficio (prazo em dias)',
                                xtype: 'numberfield',
                                allowDecimal: false,
                                width: 90,
                                style: 'text-align: right',
                                name: 'deadlineAssessmentNoticeOffice',
                                minValue: 0,
                                allowNegative: false
                            },
                            {
                                fieldLabel: 'Manifestações (prazo em dias)',
                                xtype: 'numberfield',
                                allowDecimal: false,
                                width: 90,
                                style: 'text-align: right',
                                name: 'deadlineAppeal',
                                minValue: 0,
                                allowNegative: false
                            },
                            {
                                fieldLabel: 'Carta Precatória (prazo em dias)',
                                xtype: 'numberfield',
                                allowDecimal: false,
                                width: 90,
                                style: 'text-align: right',
                                name: 'deadlineRogatoryLetter',
                                minValue: 0,
                                allowNegative: false
                            },
                            {
                                fieldLabel: 'Procedimento Preparatório Eleitoral (prazo em dias)',
                                xtype: 'numberfield',
                                allowDecimal: false,
                                width: 90,
                                style: 'text-align: right',
                                name: 'deadlinePreparatoryProcedureElectoral',
                                minValue: 0,
                                allowNegative: false
                            },
                            {
                                fieldLabel: 'Procedimento de Gestão Administrativa(prazo em dias)',
                                xtype: 'numberfield',
                                allowDecimal: false,
                                width: 90,
                                style: 'text-align: right',
                                name: 'deadlineAdministrativeManagement',
                                minValue: 0,
                                allowNegative: false
                            }
                        ]
                    },
                    this.getFieldSetTriageCenter(),
                    this.getFieldSetPortaria(),
                    this.getFieldSetDilation(),
                    this.getFieldSetBasic(),
                    this.getFieldSetCouncil(),
                    this.getFieldSetDiligence()
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
        judicial.ConfigurationManage.superclass.constructor.call(this, cfg);
        this.dataReload();
    }
});
